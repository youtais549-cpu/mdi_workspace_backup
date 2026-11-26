#!/usr/bin/env python3
r"""
run_2periods_small_vacuum_sweep.py
==============================================================================
2H-SiC {10-10} 2周期 (4層, 72原子) スラブモデルにおける
微小真空層条件 (0.75 Å, 0.25 Å, 0.0 Å) の自動構造緩和・表面破壊エネルギー算出スクリプト

【解析条件 (先ほどの計算と完全同一)】:
- 対象結晶面: 2H-SiC {10-10} 自然へき開面 (72原子, 2周期 4層, 面内 3x3)
- DFT設定: Quantum ESPRESSO 7.6 (ecutwfc=40.0 Ry, ecutrho=320.0 Ry, conv_thr=1.0e-5 Ry, Gamma点, mixing_beta=0.3)
- 緩和設定: minimize 1.0e-6 1.0e-2 100 150 (AGENTS.md §9 恒久標準)
- 並列数: 12 MPI x 2 OpenMP = 24 threads
- 成果物: md_animation.xyz, 3種推移グラフ(PNG/PDF/SVG), fracture_metadata.json
- 保存先: \\192.168.12.69\Results\yamazaki\research\{101_0}2周期〇Å
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

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
ENV_PREFIX = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
TEMPLATE_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_8periods_vac5A_natural_cleavage")
BULK_2P_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_2periods_vac5A_local_RTX5080")
CIF_INPUT = os.path.join(WORKSPACE_DIR, "research_simulations", "2H-SiC.cif")
NAS_LOCAL_STAGING_ROOT = os.path.join(WORKSPACE_DIR, "nas_staging_2periods")

# 2周期 (72原子) 真のバルク 1点 SCF エネルギー確定値
E_BULK_72_EV = -31935.3572
AREA_2A = 279.497664
CONV_FACTOR = 16.021766
EFFECTIVE_DENOM = AREA_2A / CONV_FACTOR

# 今回実行する 3 条件
TARGET_SWEEP_LIST = [
    (0.75, "0.75", "{101_0}2周期0.75Å"),
    (0.25, "0.25", "{101_0}2周期0.25Å"),
    (0.0, "0.0", "{101_0}2周期0Å"),
]

# 全23条件の一覧 (集計・サマリープロット用)
ALL_SWEEP_LIST = [
    (0.0, "0.0", "{101_0}2周期0Å"),
    (0.25, "0.25", "{101_0}2周期0.25Å"),
    (0.5, "0.5", "{101_0}2周期0.5Å"),
    (0.75, "0.75", "{101_0}2周期0.75Å"),
    (1.0, "1.0", "{101_0}2周期1Å"),
    (1.5, "1.5", "{101_0}2周期1.5Å"),
    (2.0, "2.0", "{101_0}2周期2Å"),
    (2.5, "2.5", "{101_0}2周期2.5Å"),
    (3.0, "3.0", "{101_0}2周期3.0Å"),
    (3.5, "3.5", "{101_0}2周期3.5Å"),
    (4.0, "4.0", "{101_0}2周期4.0Å"),
    (4.5, "4.5", "{101_0}2周期4.5Å"),
    (5.0, "5.0", "{101_0}2周期5.0Å"),
    (5.5, "5.5", "{101_0}2周期5.5Å"),
    (6.0, "6.0", "{101_0}2周期6.0Å"),
    (6.5, "6.5", "{101_0}2周期6.5Å"),
    (7.0, "7.0", "{101_0}2周期7.0Å"),
    (7.5, "7.5", "{101_0}2周期7.5Å"),
    (8.0, "8.0", "{101_0}2周期8Å"),
    (8.5, "8.5", "{101_0}2周期8.5Å"),
    (9.0, "9.0", "{101_0}2周期9.0Å"),
    (9.5, "9.5", "{101_0}2周期9.5Å"),
    (10.0, "10.0", "{101_0}2周期10Å"),
]


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    with open(os.path.join(WORKSPACE_DIR, "vacuum_sweep_2periods.log"), "a", encoding="utf-8") as lf:
        lf.write(line + "\n")


def prepare_condition_directory(vac_val, vac_str, nas_folder_name, port):
    """各真空層厚さ V [Å] の専用ディレクトリと入力ファイル一式を生成"""
    calc_dir_name = f"calc_2H-SiC_10-10_2periods_vac{vac_str}A_rtx5080"
    calc_dir = os.path.join(WORKSPACE_DIR, calc_dir_name)
    os.makedirs(calc_dir, exist_ok=True)

    # 1. 共通アセットの配備
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
        src_asset = os.path.join(TEMPLATE_DIR, asset)
        dst_asset = os.path.join(calc_dir, asset)
        if not os.path.exists(dst_asset):
            shutil.copyfile(src_asset, dst_asset)

    # 2周期バルクSCFログも同梱
    for bulk_file in ["2H-SiC_10-10_bulk_3x3x2_72atoms.data", "espresso_bulk_scf.pwi", "espresso_bulk_scf.pwo"]:
        src_bf = os.path.join(BULK_2P_DIR, bulk_file)
        if os.path.exists(src_bf):
            shutil.copyfile(src_bf, os.path.join(calc_dir, bulk_file))

    # 2. ASE surface() による 2周期 (4層, 72原子) 自然へき開面スラブモデルの構築
    bulk_cif = ase.io.read(CIF_INPUT)
    slab_unit = surface(bulk_cif, indices=(1, 0, 0), layers=2, vacuum=None)
    slab_3x3 = slab_unit * (3, 3, 1)

    pos = slab_3x3.positions.copy()
    z_min = float(np.min(pos[:, 2]))
    z_max = float(np.max(pos[:, 2]))
    thickness = z_max - z_min

    # 下部真空層 = vac_val [Å], 上部真空層 = vac_val [Å] (合計 2 * vac_val [Å])
    pos[:, 2] = pos[:, 2] - z_min + vac_val
    slab_3x3.positions = pos

    cell = slab_3x3.cell.copy()
    cell[2, 2] = thickness + 2.0 * vac_val
    slab_3x3.cell = cell
    slab_3x3.pbc = [True, True, True]

    # 層間間隔プロファイルの厳格検証 ([0.8881, 1.7758, 0.8881])
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 4))
    diffs = [round(float(z_unique[i + 1] - z_unique[i]), 4) for i in range(len(z_unique) - 1)]
    if len(diffs) != 3 or abs(diffs[0] - 0.8881) > 0.005 or abs(diffs[1] - 1.7758) > 0.005:
        raise RuntimeError(f"Invalid interlayer spacing profile for vac={vac_val}A: {diffs}")

    slab_prefix = f"2H-SiC_10-10_slab_3x3x2_vac{vac_str}A"
    ase.io.write(os.path.join(calc_dir, f"{slab_prefix}.cif"), slab_3x3)
    ase.io.write(os.path.join(calc_dir, f"{slab_prefix}.xyz"), slab_3x3)
    write_lammps_data(os.path.join(calc_dir, f"{slab_prefix}.data"), slab_3x3, atom_style="atomic", masses=True)

    # 3. in.lammps & in.lammps.optimized_conv の作成 (AGENTS.md §9 恒久標準)
    in_lammps_content = f"""# 2H-SiC {{10-10}} 2周期 (4層, 72原子) 真空層 {vac_str} Å スラブ構造緩和入力スクリプト
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

    # 4. fracture_metadata.json の初期化
    meta_init = {
        "model_name": f"2H-SiC_10-10_2periods_vac{vac_str}A",
        "plane": "{10-10}",
        "n_periods": 2,
        "n_layers": 4,
        "n_atoms": 72,
        "vacuum_thickness_angstrom": vac_val,
        "box_lx_ly_lz_A": [round(float(cell[0, 0]), 4), round(float(cell[1, 1]), 4), round(float(cell[2, 2]), 4)],
        "cross_sectional_area_2A_A2": round(AREA_2A, 6),
        "true_bulk_scf_energy_eV": E_BULK_72_EV,
        "convergence_settings": "minimize 1.0e-6 1.0e-2 100 150",
        "dft_settings": {
            "ecutwfc_Ry": 40.0,
            "ecutrho_Ry": 320.0,
            "conv_thr_Ry": 1.0e-5,
            "k_points": "gamma",
            "mixing_beta": 0.3,
        },
        "target_nas_folder": nas_folder_name,
        "created_at": datetime.datetime.now().isoformat(),
    }
    with open(os.path.join(calc_dir, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta_init, f, indent=4, ensure_ascii=False)

    return calc_dir, slab_prefix


def is_condition_already_converged(calc_dir):
    """既に計算が完了し、緩和後エネルギーとグラフが揃っているか判定"""
    meta_path = os.path.join(calc_dir, "fracture_metadata.json")
    log_path = os.path.join(calc_dir, "log.lammps")
    graph_path = os.path.join(calc_dir, "Total_Energy_progression.png")
    if os.path.exists(meta_path) and os.path.exists(log_path) and os.path.exists(graph_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "surface_fracture_energy_J_m2" in meta and "relaxed_slab_energy_eV" in meta:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                    if "Minimization stats:" in lf.read():
                        return True
        except Exception:
            pass
    return False


def run_single_condition(idx, total_count, vac_val, vac_str, nas_folder_name, port):
    """1つの真空層条件について構造緩和・XYZ変換・3種グラフ生成・γ算出を実行"""
    calc_dir, slab_prefix = prepare_condition_directory(vac_val, vac_str, nas_folder_name, port)

    if is_condition_already_converged(calc_dir):
        log(f"[{idx}/{total_count}] [Skip] vac={vac_str} Å ({calc_dir}) is already converged.")
        stage_and_sync_to_nas(calc_dir, nas_folder_name)
        return calc_dir

    log(f"[{idx}/{total_count}] === Starting 2-Period Slab Relaxation: Vacuum = {vac_str} Å (NAS: {nas_folder_name}) ===")

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

    elapsed = time.time() - t0
    if qe_rc != 0 or lmp_rc != 0:
        raise RuntimeError(f"MDI calculation failed for vac={vac_str}A (qe_rc={qe_rc}, lmp_rc={lmp_rc})")

    # Winmostar XYZ アニメーション生成
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=calc_dir, env=env, check=True)

    # 3種推移グラフ自動生成 (RELAXATION_GRAPH_PROTOCOL.json 準拠)
    subprocess.run([py_bin, "auto_generate_progression_graphs.py"], cwd=calc_dir, env=env, check=True)

    # エネルギーと表面破壊エネルギー γ の抽出・保存
    meta_path = os.path.join(calc_dir, "fracture_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
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
    delta_e = e_slab - E_BULK_72_EV
    gamma = delta_e / EFFECTIVE_DENOM
    diff_pct = ((gamma - 2.27) / 2.27) * 100.0

    meta["relaxed_slab_energy_eV"] = round(e_slab, 4)
    meta["delta_energy_eV"] = round(delta_e, 4)
    meta["surface_fracture_energy_J_m2"] = round(gamma, 4)
    meta["diff_percent"] = round(diff_pct, 1)
    meta["elapsed_seconds"] = round(elapsed, 1)
    meta["n_scf_steps"] = len(energies_qe)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    log(
        f"[{idx}/{total_count}] ✅ Completed vac={vac_str} Å in {elapsed/60.0:.1f} min ({len(energies_qe)} SCF evals) | "
        f"E_slab={e_slab:.4f} eV | ΔE={delta_e:.4f} eV | γ={gamma:.4f} J/m²"
    )

    # ローカルアーカイブ退避
    archive_root = os.path.join(WORKSPACE_DIR, "各条件の計算ディレクトリ")
    os.makedirs(archive_root, exist_ok=True)
    shutil.copytree(calc_dir, os.path.join(archive_root, os.path.basename(calc_dir)), dirs_exist_ok=True)

    # 総合データベース更新
    append_to_master_csv_and_md(vac_val, vac_str, e_slab, delta_e, gamma, diff_pct, os.path.basename(calc_dir))

    # NAS ステージングおよび同期
    stage_and_sync_to_nas(calc_dir, nas_folder_name)

    # 真空層依存性サマリーテーブル & 全23条件グラフ更新
    update_sweep_summary_and_graphs()
    return calc_dir


def append_to_master_csv_and_md(vac_val, vac_str, e_slab, delta_e, gamma, diff_pct, calc_dir_name):
    """surface_energy_results.csv と SURFACE_ENERGY_RESULTS.md に自動追記"""
    csv_path = os.path.join(WORKSPACE_DIR, "surface_energy_results.csv")
    md_path = os.path.join(WORKSPACE_DIR, "SURFACE_ENERGY_RESULTS.md")
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    next_no = 1
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        if calc_dir_name in "\n".join(lines):
            return
        if len(lines) > 1:
            try:
                next_no = int(lines[-1].split(",")[0]) + 1
            except ValueError:
                next_no = len(lines)

    csv_row = (
        f'{next_no},{date_str},10-10,2,4,72,{vac_val},3x3,'
        f'"CG_minimize (minimize 1.0e-6 1.0e-2 100 150)",40.0,320.0,gamma,'
        f'{e_slab:.4f},{E_BULK_72_EV:.4f},{delta_e:.4f},{AREA_2A:.4f},{gamma:.4f},'
        f'2.27,2.44,{diff_pct:+.1f},"{calc_dir_name}","calc_2H-SiC_10-10_2periods_vac5A_local_RTX5080"\n'
    )
    with open(csv_path, "a", encoding="utf-8") as f:
        f.write(csv_row)

    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_lines = f.read().splitlines()

        md_row = (
            f"| **#{next_no}** | {date_str} | `{{101_0}}` | 2 (4層) | 72 | {vac_val} Å | "
            f"`minimize 1.0e-6 1.0e-2 100 150` | {e_slab:.4f} | {E_BULK_72_EV:.4f} | {delta_e:.4f} | "
            f"**{gamma:.4f}** | 2.27〜2.44 | {diff_pct:+.1f}% | "
            f"`{calc_dir_name}`<br>`calc_2H-SiC_10-10_2periods_vac5A_local_RTX5080` |"
        )
        last_idx = -1
        for i, line in enumerate(md_lines):
            if line.strip().startswith("| **#"):
                last_idx = i
        if last_idx != -1:
            md_lines.insert(last_idx + 1, md_row)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines) + "\n")


def stage_and_sync_to_nas(calc_dir, nas_folder_name):
    """nas_staging_2periods/{nas_folder_name} へローカル退避"""
    os.makedirs(NAS_LOCAL_STAGING_ROOT, exist_ok=True)
    local_nas_dir = os.path.join(NAS_LOCAL_STAGING_ROOT, nas_folder_name)
    if os.path.exists(local_nas_dir):
        shutil.rmtree(local_nas_dir)
    shutil.copytree(calc_dir, local_nas_dir)
    log(f"  -> Staged locally at: {local_nas_dir} (ready for NAS batch sync)")


def update_sweep_summary_and_graphs():
    """完了済みの全真空層条件 (最大23条件) を集計し、CSVおよび全3形式のデフォルトグラフを自動出力"""
    collected = []
    for vac_val, vac_str, nas_folder_name in ALL_SWEEP_LIST:
        calc_dir = os.path.join(WORKSPACE_DIR, f"calc_2H-SiC_10-10_2periods_vac{vac_str}A_rtx5080")
        meta_path = os.path.join(calc_dir, "fracture_metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if "surface_fracture_energy_J_m2" in meta and "relaxed_slab_energy_eV" in meta:
                    collected.append(
                        (
                            vac_val,
                            vac_str,
                            nas_folder_name,
                            meta["relaxed_slab_energy_eV"],
                            meta["true_bulk_scf_energy_eV"],
                            meta["delta_energy_eV"],
                            meta["surface_fracture_energy_J_m2"],
                            meta.get("elapsed_seconds", 0.0),
                        )
                    )
            except Exception:
                pass

    if not collected:
        return

    collected.sort(key=lambda x: x[0])

    # 1. CSV更新 (0.5〜10A 互換用 & 全条件用)
    csv_paths = [
        os.path.join(WORKSPACE_DIR, "vacuum_sweep_2periods_0.5_to_10A_results.csv"),
        os.path.join(WORKSPACE_DIR, "vacuum_sweep_2periods_results.csv"),
    ]
    for cp in csv_paths:
        with open(cp, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "Vacuum_A",
                    "NAS_Folder",
                    "E_slab_eV",
                    "E_bulk_eV",
                    "Delta_E_eV",
                    "Area_2A_A2",
                    "Gamma_J_m2",
                    "Elapsed_s",
                ]
            )
            for v_val, v_str, n_folder, es, eb, de, g, el in collected:
                w.writerow([v_val, n_folder, es, eb, de, round(AREA_2A, 4), g, el])

    # 2. 全3種類の承認済みデフォルトグラフ自動更新
    try:
        py_bin = os.path.join(ENV_PREFIX, "bin", "python3")
        gen_script = os.path.join(WORKSPACE_DIR, "generate_default_surface_energy_graphs.py")
        subprocess.run([py_bin, gen_script], cwd=WORKSPACE_DIR, check=True)
    except Exception as e:
        log(f"Notice: Failed to regenerate default graphs: {e}")


def main():
    total_count = len(TARGET_SWEEP_LIST)
    log(f"🚀 Starting small vacuum sweep for 2H-SiC {{10-10}} 2-period slab ({total_count} conditions: 0.75 Å, 0.25 Å, 0.0 Å)")

    base_port = 8060
    for idx, (vac_val, vac_str, nas_folder_name) in enumerate(TARGET_SWEEP_LIST, start=1):
        port = base_port + idx
        try:
            run_single_condition(idx, total_count, vac_val, vac_str, nas_folder_name, port)
        except Exception as e:
            log(f"[{idx}/{total_count}] ❌ Error on vac={vac_str} Å: {e}")

    log("🎉 Small vacuum sweep calculations completed!")


if __name__ == "__main__":
    main()

