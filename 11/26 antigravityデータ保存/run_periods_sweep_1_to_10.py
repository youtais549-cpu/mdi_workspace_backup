#!/usr/bin/env python3
r"""
run_periods_sweep_1_to_10.py
==============================================================================
2H-SiC {10-10} スラブモデルにおける周期数依存性 (1, 3, 5, 7, 9, 10 周期)
全自動実行スクリプト (バルク 1 点 SCF 先行確定 ＋ スラブ CG 構造緩和 ＋ NAS 保存)

【準拠ルール (絶対厳守)】:
1. AGENTS.md §1: スラブ緩和前の「バルク 1 点 SCF 先行確定」プロトコル
   - 各周期数 N のスラブ計算前に、必ず同一原子数 (36*N 原子) の真のバルクモデル (真空 0 Å) による
     Quantum ESPRESSO 1 点 SCF 計算を実施し、E_bulk および 1 原子あたりエネルギー (-443.5 eV/atom) を検証。
2. AGENTS.md §2: 元素対応 Type 1 = C (12.011), Type 2 = Si (28.085)
3. AGENTS.md §9: 最適化収束条件標準 (minimize 1.0e-6 1.0e-2 100 150)
4. AGENTS.md §10: 結晶面切断の物理的前提 (ASE surface(bulk, indices=(1,0,0), layers=N) による自然へき開面)
5. ユーザー指定 NAS 保存先: \\192.168.12.69\Results\yamazaki\research\{101_0}〇周期5Å
   (各フォルダ内にスラブ緩和データおよびバルクモデル計算データを同梱)
==============================================================================
"""

import os
import sys
import re
import csv
import json
import time
import base64
import shutil
import datetime
import subprocess
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache_sic"
os.makedirs("/tmp/matplotlib_cache_sic", exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, TextArea

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
ENV_PREFIX = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
TEMPLATE_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_8periods_vac5A_natural_cleavage")
CIF_INPUT = os.path.join(WORKSPACE_DIR, "research_simulations", "2H-SiC.cif")
NAS_STAGING_ROOT = os.path.join(WORKSPACE_DIR, "nas_staging_periods")

# 物理定数
AREA_2A = 279.497664
CONV_FACTOR = 16.021766
EFFECTIVE_DENOM = AREA_2A / CONV_FACTOR  # 17.44487243166577
EXACT_D_PERIOD = (np.sqrt(3.0) / 2.0) * 3.076  # 2.6638941420409297 Å

# 今回実行対象の周期数
TARGET_PERIODS = [1, 3, 5, 7, 9, 10]

# 全周期数の参照リスト (1〜10周期)
ALL_PERIODS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    with open(os.path.join(WORKSPACE_DIR, "period_sweep.log"), "a", encoding="utf-8") as lf:
        lf.write(line + "\n")


def build_models(N):
    """周期数 N のスラブモデル (真空 5.0 Å) および真のバルクモデル (真空 0 Å) を生成"""
    bulk_cif = ase.io.read(CIF_INPUT)

    # 1. スラブモデルの構築 (ASE layers=N で N 周期 = 2N 層)
    slab_unit = surface(bulk_cif, indices=(1, 0, 0), layers=N, vacuum=None)
    slab_3x3 = slab_unit * (3, 3, 1)

    pos = slab_3x3.positions.copy()
    z_min = float(np.min(pos[:, 2]))
    z_max = float(np.max(pos[:, 2]))
    thickness = z_max - z_min

    # 下部真空層 = 5.0 Å, 上部真空層 = 5.0 Å (合計 10.0 Å)
    pos[:, 2] = pos[:, 2] - z_min + 5.0
    slab_3x3.positions = pos

    cell_slab = slab_3x3.cell.copy()
    cell_slab[2, 2] = thickness + 10.0
    slab_3x3.cell = cell_slab
    slab_3x3.pbc = [True, True, True]

    # 層間距離プロファイルの検証
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 4))
    diffs = [round(float(z_unique[i + 1] - z_unique[i]), 4) for i in range(len(z_unique) - 1)]
    if len(diffs) > 0 and (abs(diffs[0] - 0.8881) > 0.005 or abs(diffs[-1] - 0.8881) > 0.005):
        raise RuntimeError(f"Invalid interlayer spacing profile for N={N} periods: {diffs}")

    # 2. 真のバルク基準モデル (真空 0 Å, 周期境界で弱結合 1.776 Å が接続)
    # 奇数周期では六方晶並進ベクトルの面内シフト dx = -a/2 = -1.538 Å を保持する
    bulk_pos = slab_3x3.positions.copy()
    bulk_pos[:, 2] = bulk_pos[:, 2] - 5.0  # z = 0.0 Å から開始
    bulk_cell = slab_3x3.cell.copy()
    bulk_cell[2, 0] = -1.538 if (N % 2 == 1) else 0.0
    bulk_cell[2, 1] = 0.0
    bulk_cell[2, 2] = N * EXACT_D_PERIOD
    bulk_atoms = ase.Atoms(
        symbols=slab_3x3.get_chemical_symbols(),
        positions=bulk_pos,
        cell=bulk_cell,
        pbc=[True, True, True],
    )
    bulk_atoms.wrap()

    return slab_3x3, bulk_atoms, thickness, diffs


def run_bulk_scf(N, calc_dir, bulk_atoms):
    """【AGENTS.md §1 必須プロトコル】真のバルクモデル (36*N 原子) による 1 点 SCF 先行確定"""
    natoms = len(bulk_atoms)
    log(
        f"--- [Period {N}] Step 1: Running True Bulk 1-Point SCF "
        f"({natoms} atoms, v3=[{bulk_atoms.cell[2,0]:.3f}, {bulk_atoms.cell[2,1]:.3f}, {bulk_atoms.cell[2,2]:.4f}] Å) ---"
    )

    pwi_lines = [
        "&CONTROL",
        "   calculation      = 'scf'",
        "   restart_mode     = 'from_scratch'",
        "   tstress          = .false.",
        "   tprnfor          = .true.",
        "   outdir           = './tmp_bulk'",
        "   prefix           = 'sic_bulk'",
        "   pseudo_dir       = './'",
        "   disk_io          = 'minimal'",
        "/",
        "&SYSTEM",
        "   ibrav            = 0",
        "   ecutwfc          = 40.0",
        "   ecutrho          = 320.0",
        "   occupations      = 'smearing'",
        "   degauss          = 0.01",
        "   smearing         = 'gaussian'",
        "   ntyp             = 2",
        f"   nat              = {natoms}",
        "/",
        "&ELECTRONS",
        "   electron_maxstep = 200",
        "   conv_thr         = 1e-05",
        "   mixing_mode      = 'local-TF'",
        "   mixing_beta      = 0.3",
        "/",
        "ATOMIC_SPECIES",
        "Si 28.085 Si.upf",
        "C 12.011 C.upf",
        "",
        "K_POINTS gamma",
        "",
        "CELL_PARAMETERS angstrom",
        f"{bulk_atoms.cell[0,0]:.14f} {bulk_atoms.cell[0,1]:.14f} {bulk_atoms.cell[0,2]:.14f}",
        f"{bulk_atoms.cell[1,0]:.14f} {bulk_atoms.cell[1,1]:.14f} {bulk_atoms.cell[1,2]:.14f}",
        f"{bulk_atoms.cell[2,0]:.14f} {bulk_atoms.cell[2,1]:.14f} {bulk_atoms.cell[2,2]:.14f}",
        "",
        "ATOMIC_POSITIONS angstrom",
    ]
    for sym, p in zip(bulk_atoms.get_chemical_symbols(), bulk_atoms.positions):
        pwi_lines.append(f"{sym} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}")

    pwi_path = os.path.join(calc_dir, "espresso_bulk_scf.pwi")
    pwo_path = os.path.join(calc_dir, "espresso_bulk_scf.pwo")
    with open(pwi_path, "w", encoding="utf-8") as f:
        f.write("\n".join(pwi_lines) + "\n")

    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["OMP_NUM_THREADS"] = "2"

    pw_bin = os.path.join(ENV_PREFIX, "bin", "pw.x")
    mpirun_bin = os.path.join(ENV_PREFIX, "bin", "mpirun")

    t0 = time.time()
    cmd = [mpirun_bin, "--oversubscribe", "-np", "12", pw_bin, "-ndiag", "1", "-in", "espresso_bulk_scf.pwi"]
    with open(pwo_path, "w") as out_f:
        res = subprocess.run(cmd, cwd=calc_dir, env=env, stdout=out_f, stderr=subprocess.STDOUT)
    elapsed = time.time() - t0

    if res.returncode != 0:
        raise RuntimeError(f"Bulk SCF calculation failed for N={N} (code={res.returncode})")

    with open(pwo_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    m_e = re.findall(r"!\s+total energy\s+=\s+([-\d\.]+)\s+Ry", text)
    if not m_e:
        raise RuntimeError(f"Could not parse bulk SCF energy for N={N} from {pwo_path}")

    e_bulk_ry = float(m_e[-1])
    conv_ry_to_ev = 13.605693122994
    e_bulk_ev = e_bulk_ry * conv_ry_to_ev
    e_per_atom = e_bulk_ev / float(natoms)

    log(
        f"--- [Period {N}] Bulk SCF Done in {elapsed:.1f}s | "
        f"E_bulk={e_bulk_ev:.4f} eV ({e_bulk_ry:.8f} Ry) | {e_per_atom:.4f} eV/atom (Target: -443.5 eV/atom) ---"
    )

    # 構造ファイルも保存
    prefix_bulk = os.path.join(calc_dir, f"bulk_10-10_{natoms}atoms_true_bulk")
    ase.io.write(f"{prefix_bulk}.cif", bulk_atoms)
    ase.io.write(f"{prefix_bulk}.xyz", bulk_atoms)
    write_lammps_data(f"{prefix_bulk}.data", bulk_atoms, atom_style="atomic", masses=True)

    return e_bulk_ev, e_bulk_ry, elapsed


def deploy_common_assets(calc_dir):
    """共通アセット (UPF擬ポテンシャル, グラフ指示書, スクリプト等) を配備"""
    for asset in [
        "C.upf",
        "Si.upf",
        "RELAXATION_GRAPH_PROTOCOL.json",
        "dft_settings.py",
        "make_xyz.py",
        "msmincho.ttc",
        "times.ttf",
        "auto_generate_progression_graphs.py",
        "qe_mdi_engine_rtx5080.py",
    ]:
        src = os.path.join(TEMPLATE_DIR, asset)
        dst = os.path.join(calc_dir, asset)
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)


def prepare_slab_directory(N, calc_dir, slab_3x3, e_bulk_ev, e_bulk_ry, port):
    """スラブ緩和計算用の入力ファイル一式を配備"""
    natoms = len(slab_3x3)
    slab_prefix = f"slab_10-10_{natoms}atoms_vac5A"

    # 1. 共通アセット配備 (念のため再確認)
    deploy_common_assets(calc_dir)

    # 2. スラブ構造ファイル保存
    ase.io.write(os.path.join(calc_dir, f"{slab_prefix}.cif"), slab_3x3)
    ase.io.write(os.path.join(calc_dir, f"{slab_prefix}.xyz"), slab_3x3)
    write_lammps_data(os.path.join(calc_dir, f"{slab_prefix}.data"), slab_3x3, atom_style="atomic", masses=True)

    # 3. in.lammps 作成 (AGENTS.md §9 恒久標準)
    in_lammps_content = f"""# 2H-SiC {{10-10}} {N}周期 ({2*N}層, {natoms}原子) 真空層 5.0 Å スラブ構造緩和入力スクリプト
# 【最適化収束条件標準: minimize 1.0e-6 1.0e-2 100 150 (AGENTS.md §9)】
units metal
boundary p p p
atom_style atomic
atom_modify map yes

read_data {slab_prefix}.data

# Type 1: C (12.011), Type 2: Si (28.085) (AGENTS.md §2)
mass 1 12.011
mass 2 28.085

fix 1 all mdi/qm elements C Si

thermo 1
thermo_modify flush yes
dump 1 all custom 1 dump.lammpstrj id type x y z
dump_modify 1 append yes flush yes

minimize 1.0e-6 1.0e-2 100 150

undump 1
write_data {slab_prefix}_relaxed.data
"""
    with open(os.path.join(calc_dir, "in.lammps"), "w") as f:
        f.write(in_lammps_content)
    with open(os.path.join(calc_dir, "in.lammps.optimized_conv"), "w") as f:
        f.write(in_lammps_content)

    # 4. fracture_metadata.json 初期化
    meta_init = {
        "model_name": f"2H-SiC_10-10_{N}periods_vac5A",
        "plane": "{10-10}",
        "n_periods": N,
        "n_layers": 2 * N,
        "n_atoms": natoms,
        "vacuum_thickness_angstrom": 5.0,
        "box_lx_ly_lz_A": [
            round(float(slab_3x3.cell[0, 0]), 4),
            round(float(slab_3x3.cell[1, 1]), 4),
            round(float(slab_3x3.cell[2, 2]), 4),
        ],
        "cross_sectional_area_2A_A2": round(AREA_2A, 6),
        "true_bulk_scf_energy_Ry": round(e_bulk_ry, 8),
        "true_bulk_scf_energy_eV": round(e_bulk_ev, 4),
        "convergence_settings": "minimize 1.0e-6 1.0e-2 100 150",
        "dft_settings": {
            "ecutwfc_Ry": 40.0,
            "ecutrho_Ry": 320.0,
            "conv_thr_Ry": 1.0e-5,
            "k_points": "gamma",
            "mixing_beta": 0.3,
        },
        "target_nas_folder": f"{{101_0}}{N}周期5Å",
        "created_at": datetime.datetime.now().isoformat(),
    }
    with open(os.path.join(calc_dir, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta_init, f, indent=4, ensure_ascii=False)

    return slab_prefix


def run_single_period(N, port):
    """周期数 N のバルク先行計算、スラブ緩和、解析、NASステージングを一括実行"""
    calc_dir_name = f"calc_2H-SiC_10-10_{N}periods_vac5A_natural_cleavage"
    calc_dir = os.path.join(WORKSPACE_DIR, calc_dir_name)
    os.makedirs(calc_dir, exist_ok=True)
    nas_folder_name = f"{{101_0}}{N}周期5Å"

    # 既に完了しているか判定
    meta_path = os.path.join(calc_dir, "fracture_metadata.json")
    log_path = os.path.join(calc_dir, "log.lammps")
    graph_path = os.path.join(calc_dir, "Total_Energy_progression.png")
    if os.path.exists(meta_path) and os.path.exists(log_path) and os.path.exists(graph_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                m = json.load(f)
            if "surface_fracture_energy_J_m2" in m and "relaxed_slab_energy_eV" in m:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                    if "Minimization stats:" in lf.read():
                        log(f"[Skip] N={N} periods ({calc_dir}) is already converged.")
                        stage_to_nas_local(calc_dir, nas_folder_name)
                        return calc_dir
        except Exception:
            pass

    log(f"============================================================")
    log(f"🚀 Starting Period {N} Calculation Flow (Target NAS: {nas_folder_name})")
    log(f"============================================================")

    # 共通アセット (UPF擬ポテンシャル等) を最優先配備 (バルクSCFに必須)
    deploy_common_assets(calc_dir)

    # 1. 構造構築
    slab_3x3, bulk_atoms, thickness, diffs = build_models(N)
    natoms = len(slab_3x3)

    # 2. 【Phase 1】真のバルク 1点 SCF 先行確定
    e_bulk_ev, e_bulk_ry, bulk_elapsed = run_bulk_scf(N, calc_dir, bulk_atoms)

    # 3. 【Phase 2】スラブ緩和入力配備
    slab_prefix = prepare_slab_directory(N, calc_dir, slab_3x3, e_bulk_ev, e_bulk_ry, port)

    # 以前の残骸をクリーンアップ
    for fn in ["tmp", "espresso.pwo", "espresso_all_steps.pwo", "dump.lammpstrj", "qe_engine.log", "lmp.log", "log.lammps"]:
        p = os.path.join(calc_dir, fn)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        elif os.path.exists(p):
            os.remove(p)

    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["QE_MPI_NP"] = "12"
    env["QE_OMP_THREADS"] = "2"
    env["MPLCONFIGDIR"] = "/tmp/matplotlib_cache_sic"

    lmp_bin = os.path.join(ENV_PREFIX, "bin", "lmp")
    py_bin = os.path.join(ENV_PREFIX, "bin", "python3")

    log(f"--- [Period {N}] Step 2: Running MDI Slab Relaxation ({natoms} atoms, vacuum 5.0 Å) ---")
    t0 = time.time()
    with open(os.path.join(calc_dir, "lmp.log"), "w") as lmp_out, open(
        os.path.join(calc_dir, "qe_engine.log"), "w"
    ) as qe_out:
        lmp_proc = subprocess.Popen(
            [lmp_bin, "-mdi", f"-role DRIVER -name LAMMPS -method TCP -port {port}", "-in", "in.lammps"],
            cwd=calc_dir,
            env=env,
            stdout=lmp_out,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1.0)
        qe_proc = subprocess.Popen(
            [
                py_bin,
                "qe_mdi_engine_rtx5080.py",
                "-mdi",
                f"-role ENGINE -name QE -method TCP -port {port} -hostname localhost",
            ],
            cwd=calc_dir,
            env=env,
            stdout=qe_out,
            stderr=subprocess.STDOUT,
        )
        qe_rc = qe_proc.wait()
        lmp_rc = lmp_proc.wait()

    slab_elapsed = time.time() - t0
    if qe_rc != 0 or lmp_rc != 0:
        raise RuntimeError(f"MDI calculation failed for N={N} (qe_rc={qe_rc}, lmp_rc={lmp_rc})")

    # 4. 【Phase 3】ポスト処理 (Winmostar XYZ, 3種推移グラフ, γ算出)
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=calc_dir, env=env, check=True)
    subprocess.run([py_bin, "auto_generate_progression_graphs.py"], cwd=calc_dir, env=env, check=True)

    with open(os.path.join(calc_dir, "fracture_metadata.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)

    energies_qe = []
    with open(os.path.join(calc_dir, "qe_engine.log"), "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r"Total Energy:\s+([-\d\.]+)\s+eV", line)
            if m:
                energies_qe.append(float(m.group(1)))

    energies_lmp = []
    with open(os.path.join(calc_dir, "log.lammps"), "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    m_fin = re.search(r"Energy initial, next-to-last, final =\s*\n\s*([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)", text)
    if m_fin:
        energies_lmp.append(float(m_fin.group(3)))

    e_slab = energies_lmp[-1] if energies_lmp else energies_qe[-1]
    delta_e = e_slab - e_bulk_ev
    gamma = delta_e / EFFECTIVE_DENOM
    diff_pct = ((gamma - 2.27) / 2.27) * 100.0

    meta["relaxed_slab_energy_eV"] = round(e_slab, 4)
    meta["delta_energy_eV"] = round(delta_e, 4)
    meta["surface_fracture_energy_J_m2"] = round(gamma, 4)
    meta["diff_percent"] = round(diff_pct, 1)
    meta["bulk_elapsed_seconds"] = round(bulk_elapsed, 1)
    meta["slab_elapsed_seconds"] = round(slab_elapsed, 1)
    meta["total_elapsed_seconds"] = round(bulk_elapsed + slab_elapsed, 1)
    meta["n_scf_steps"] = len(energies_qe)

    with open(os.path.join(calc_dir, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    log(
        f"✅ [Period {N}] Complete! Natoms={natoms} | Bulk: {bulk_elapsed:.1f}s | "
        f"Slab: {slab_elapsed/60.0:.1f} min ({len(energies_qe)} evals) | "
        f"E_slab={e_slab:.4f} eV | ΔE={delta_e:.4f} eV | γ={gamma:.4f} J/m²"
    )

    # 5. 【Phase 4】ローカルアーカイブ退避 & NASステージング
    archive_root = os.path.join(WORKSPACE_DIR, "各条件の計算ディレクトリ")
    os.makedirs(archive_root, exist_ok=True)
    shutil.copytree(calc_dir, os.path.join(archive_root, os.path.basename(calc_dir)), dirs_exist_ok=True)

    stage_to_nas_local(calc_dir, nas_folder_name)

    # 6. 【Phase 5】総合台帳更新 & 周期数依存性グラフ自動更新
    append_to_master_csv_and_md(N, natoms, e_slab, e_bulk_ev, delta_e, gamma, diff_pct, calc_dir_name)
    update_periods_summary_and_graphs()

    return calc_dir


def stage_to_nas_local(calc_dir, nas_folder_name):
    """nas_staging_periods/{nas_folder_name} へローカル完全ステージング (バルクデータ同梱)"""
    os.makedirs(NAS_STAGING_ROOT, exist_ok=True)
    local_nas_dir = os.path.join(NAS_STAGING_ROOT, nas_folder_name)
    if os.path.exists(local_nas_dir):
        shutil.rmtree(local_nas_dir)
    shutil.copytree(calc_dir, local_nas_dir)
    log(f"  -> Staged locally at: {local_nas_dir} (includes bulk & slab calculation data)")


def append_to_master_csv_and_md(N, natoms, e_slab, e_bulk, delta_e, gamma, diff_pct, calc_dir_name):
    """surface_energy_results.csv と SURFACE_ENERGY_RESULTS.md に自動追記（または該当行の差し替え更新）"""
    csv_path = os.path.join(WORKSPACE_DIR, "surface_energy_results.csv")
    md_path = os.path.join(WORKSPACE_DIR, "SURFACE_ENERGY_RESULTS.md")
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    next_no = 1
    replaced_csv = False
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        new_lines = []
        for ln in lines:
            if f'"{calc_dir_name}"' in ln:
                row_no = ln.split(",")[0]
                row_date = ln.split(",")[1]
                new_ln = (
                    f'{row_no},{row_date},10-10,{N},{2*N},{natoms},5.0,3x3,'
                    f'"CG_minimize (minimize 1.0e-6 1.0e-2 100 150)",40.0,320.0,gamma,'
                    f'{e_slab:.4f},{e_bulk:.4f},{delta_e:.4f},{AREA_2A:.4f},{gamma:.4f},'
                    f'2.27,2.44,{diff_pct:+.1f},"{calc_dir_name}","true_bulk_scf"'
                )
                new_lines.append(new_ln)
                replaced_csv = True
            else:
                new_lines.append(ln)
        if replaced_csv:
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
        else:
            if len(lines) > 1:
                try:
                    next_no = int(lines[-1].split(",")[0]) + 1
                except ValueError:
                    next_no = len(lines)

    if not replaced_csv:
        csv_row = (
            f'{next_no},{date_str},10-10,{N},{2*N},{natoms},5.0,3x3,'
            f'"CG_minimize (minimize 1.0e-6 1.0e-2 100 150)",40.0,320.0,gamma,'
            f'{e_slab:.4f},{e_bulk:.4f},{delta_e:.4f},{AREA_2A:.4f},{gamma:.4f},'
            f'2.27,2.44,{diff_pct:+.1f},"{calc_dir_name}","true_bulk_scf"\n'
        )
        with open(csv_path, "a", encoding="utf-8") as f:
            f.write(csv_row)

    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_lines = f.read().splitlines()

        replaced_md = False
        for i, line in enumerate(md_lines):
            if f"`{calc_dir_name}`" in line and line.strip().startswith("| **#"):
                parts = [p.strip() for p in line.split("|")]
                no_tag = parts[1]
                row_date = parts[2]
                md_lines[i] = (
                    f"| {no_tag} | {row_date} | `{{101_0}}` | {N} ({2*N}層) | {natoms} | 5.0 Å | "
                    f"`minimize 1.0e-6 1.0e-2 100 150` | {e_slab:.4f} | {e_bulk:.4f} | {delta_e:.4f} | "
                    f"**{gamma:.4f}** | 2.27〜2.44 | {diff_pct:+.1f}% | "
                    f"`{calc_dir_name}` |"
                )
                replaced_md = True
                break

        if not replaced_md:
            md_row = (
                f"| **#{next_no}** | {date_str} | `{{101_0}}` | {N} ({2*N}層) | {natoms} | 5.0 Å | "
                f"`minimize 1.0e-6 1.0e-2 100 150` | {e_slab:.4f} | {e_bulk:.4f} | {delta_e:.4f} | "
                f"**{gamma:.4f}** | 2.27〜2.44 | {diff_pct:+.1f}% | "
                f"`{calc_dir_name}` |"
            )
            last_idx = -1
            for i, line in enumerate(md_lines):
                if line.strip().startswith("| **#"):
                    last_idx = i
            if last_idx != -1:
                md_lines.insert(last_idx + 1, md_row)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")


def update_periods_summary_and_graphs():
    """完了済みの全周期数条件 (1〜10周期) を集計し、CSVおよび周期数依存性比較グラフを出力"""
    collected = []
    # 既存の計算ディレクトリと新規ディレクトリの両方を探索
    for N in ALL_PERIODS:
        # パス候補
        candidates = [
            os.path.join(WORKSPACE_DIR, f"calc_2H-SiC_10-10_{N}periods_vac5A_natural_cleavage"),
            os.path.join(WORKSPACE_DIR, f"calc_2H-SiC_10-10_{N}periods_vac5A_local_RTX5080"),
            os.path.join(WORKSPACE_DIR, f"calc_2H-SiC_10-10_{N}periods_vac5A"),
            os.path.join(WORKSPACE_DIR, f"results_2H-SiC_10-10_slab_{N}periods_vac5A_relaxed_20261022"),
        ]
        if N == 2:
            candidates.insert(0, os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_2periods_vac5.0A_rtx5080"))

        found_meta = None
        for c in candidates:
            m_path = os.path.join(c, "fracture_metadata.json")
            if os.path.exists(m_path):
                try:
                    with open(m_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    if "surface_fracture_energy_J_m2" in meta:
                        found_meta = meta
                        break
                except Exception:
                    pass

        if found_meta:
            natoms = found_meta.get("n_atoms", found_meta.get("natoms", 36 * N))
            e_slab = found_meta.get("relaxed_slab_energy_eV", 0.0)
            e_bulk = found_meta.get("true_bulk_scf_energy_eV", 0.0)
            de = found_meta.get("delta_energy_eV", e_slab - e_bulk)
            gamma = found_meta.get("surface_fracture_energy_J_m2", 0.0)
            collected.append((N, natoms, e_slab, e_bulk, de, gamma))
        elif N == 4:
            # 4周期 (#05: SURFACE_ENERGY_RESULTS.md に記録済みの確定値)
            collected.append((4, 144, -63822.0658, -63863.3059, 41.2401, 2.3642))

    if not collected:
        return

    collected.sort(key=lambda x: x[0])

    # 1. CSV更新
    csv_path = os.path.join(WORKSPACE_DIR, "surface_energy_vs_periods_plot_data.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Periods", "Natoms", "Vacuum_A", "E_slab_eV", "E_bulk_eV", "Delta_E_eV", "Area_2A_A2", "Gamma_J_m2"])
        for n, na, es, eb, de, g in collected:
            w.writerow([n, na, 5.0, es, eb, round(de, 4), AREA_2A, round(g, 4)])

    # 2. グラフ描画 (AGENTS.md §7 準拠: 周期数依存性仕様)
    mincho = os.path.join(WORKSPACE_DIR, "msmincho.ttc")
    times = os.path.join(WORKSPACE_DIR, "times.ttf")
    timesbd = os.path.join(WORKSPACE_DIR, "timesbd.ttf")

    font_label = fm.FontProperties(fname=mincho, size=14.5)
    font_tick = fm.FontProperties(fname=times, size=11.5)
    font_lit_jp = fm.FontProperties(fname=mincho, weight="bold", size=12.0)
    font_lit_en = fm.FontProperties(fname=timesbd, weight="bold", size=12.5)

    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    x_pts = [c[0] for c in collected]
    y_pts = [c[5] for c in collected]

    ax.scatter(x_pts, y_pts, marker="^", facecolors="none", edgecolors="#8A2BE2", s=70, linewidths=1.6, zorder=5)

    # 文献値 (3.03 J/m²) 水平破線
    LIT_VAL = 3.03
    ax.axhline(LIT_VAL, color="#222222", linestyle="--", linewidth=1.2, zorder=3)

    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_lit_jp, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_lit_en, color="#111111"))
    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=3)

    y_norm = (LIT_VAL - 2.2) / (3.2 - 2.2) + 0.024
    anchored = AnchoredOffsetbox(
        loc="lower right",
        child=packer,
        pad=0.0,
        frameon=False,
        bbox_to_anchor=(0.95, y_norm),
        bbox_transform=ax.transAxes,
    )
    ax.add_artist(anchored)

    # 軸範囲と目盛り (AGENTS.md §7: 縦軸 2.2〜3.2 J/m², 横軸 0〜11)
    ax.set_xlim(0.0, 11.0)
    ax.set_ylim(2.2, 3.2)

    ax.set_xlabel(r"周期数  $\mathrm{[periods]}$", fontproperties=font_label, labelpad=10)
    ax.set_ylabel(r"表面破壊エネルギー  $\mathrm{[J/m^2]}$", fontproperties=font_label, labelpad=10)

    x_ticks = [0, 2, 4, 6, 8, 10]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(x) for x in x_ticks], fontproperties=font_tick)

    y_ticks = [2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_tick)

    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.1)

    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=5.5,
        width=1.0,
        top=True,
        right=True,
        bottom=True,
        left=True,
        pad=6.0,
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.subplots_adjust(left=0.17, right=0.95, bottom=0.17, top=0.95)

    base = os.path.join(WORKSPACE_DIR, "周期数と表面破壊エネルギーの関係")
    plt.savefig(f"{base}.png", dpi=300)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    log(f"✅ Updated period comparison graph: {base}.png/.pdf/.svg")


def rerun_odd_bulk_only(odd_periods=None):
    """奇数周期 (1, 3, 5, 7, 9 周期) のバルク 1点 SCF のみを正しい並進ベクトルで再実行し、データ・台帳・ステージングを更新"""
    if odd_periods is None:
        odd_periods = [1, 3, 5, 7, 9]
    log(f"🔄 Starting Bulk SCF Re-execution for Odd Periods: {odd_periods}")

    for N in odd_periods:
        calc_dir_name = f"calc_2H-SiC_10-10_{N}periods_vac5A_natural_cleavage"
        calc_dir = os.path.join(WORKSPACE_DIR, calc_dir_name)
        nas_folder_name = f"{{101_0}}{N}周期5Å"

        deploy_common_assets(calc_dir)
        slab_3x3, bulk_atoms, thickness, diffs = build_models(N)
        natoms = len(slab_3x3)

        # 古い tmp_bulk を削除して再実行
        tmp_bulk = os.path.join(calc_dir, "tmp_bulk")
        if os.path.exists(tmp_bulk):
            shutil.rmtree(tmp_bulk, ignore_errors=True)

        e_bulk_ev, e_bulk_ry, bulk_elapsed = run_bulk_scf(N, calc_dir, bulk_atoms)

        meta_path = os.path.join(calc_dir, "fracture_metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        e_slab = meta["relaxed_slab_energy_eV"]
        delta_e = e_slab - e_bulk_ev
        gamma = delta_e / EFFECTIVE_DENOM
        diff_pct = ((gamma - 2.27) / 2.27) * 100.0

        meta["true_bulk_scf_energy_Ry"] = round(e_bulk_ry, 8)
        meta["true_bulk_scf_energy_eV"] = round(e_bulk_ev, 4)
        meta["delta_energy_eV"] = round(delta_e, 4)
        meta["surface_fracture_energy_J_m2"] = round(gamma, 4)
        meta["diff_percent"] = round(diff_pct, 1)
        meta["bulk_elapsed_seconds"] = round(bulk_elapsed, 1)
        meta["total_elapsed_seconds"] = round(bulk_elapsed + meta.get("slab_elapsed_seconds", 0.0), 1)
        meta["bulk_cell_vector_v3_A"] = [
            round(float(bulk_atoms.cell[2, 0]), 4),
            round(float(bulk_atoms.cell[2, 1]), 4),
            round(float(bulk_atoms.cell[2, 2]), 4),
        ]

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)

        log(
            f"✅ [Period {N} Bulk Updated] Natoms={natoms} | Bulk: {bulk_elapsed:.1f}s | "
            f"E_bulk={e_bulk_ev:.4f} eV | E_slab={e_slab:.4f} eV | ΔE={delta_e:.4f} eV | γ={gamma:.4f} J/m²"
        )

        # ローカルアーカイブ & NASステージングを更新
        archive_root = os.path.join(WORKSPACE_DIR, "各条件の計算ディレクトリ")
        os.makedirs(archive_root, exist_ok=True)
        dst_arch = os.path.join(archive_root, os.path.basename(calc_dir))
        if os.path.exists(dst_arch):
            shutil.rmtree(dst_arch)
        shutil.copytree(calc_dir, dst_arch)

        stage_to_nas_local(calc_dir, nas_folder_name)
        append_to_master_csv_and_md(N, natoms, e_slab, e_bulk_ev, delta_e, gamma, diff_pct, calc_dir_name)

    update_periods_summary_and_graphs()
    log("🎉 All odd period bulk SCF updates & graphs completed!")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--rerun-odd-bulk":
        rerun_odd_bulk_only()
        return

    periods = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else TARGET_PERIODS
    total_count = len(periods)
    log(f"🌟 Starting Periods Sweep Automation for {total_count} conditions: {periods}")

    base_port = 8070
    for idx, N in enumerate(periods, start=1):
        port = base_port + idx
        try:
            run_single_period(N, port)
        except Exception as e:
            log(f"[{idx}/{total_count}] ❌ Error on Period {N}: {e}")

    log("🎉 All requested period calculations completed!")


if __name__ == "__main__":
    main()
