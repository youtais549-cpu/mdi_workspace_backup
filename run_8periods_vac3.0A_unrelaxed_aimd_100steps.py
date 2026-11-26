#!/usr/bin/env python3
r"""
run_8periods_vac3.0A_unrelaxed_aimd_100steps.py
==============================================================================
2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 3.0 Å (スラブ間ギャップ 6.0 Å)
【構造最適化なし (未緩和スラブ初期構造)】からの 300 K NVT 第一原理分子動力学 (AIMD 100 steps = 100 fs)

・初期構造以外は前回の AIMD (aimd_2H-SiC_10-10_8periods_vac3.0A_300K_100steps_rtx5080) と完全同一条件
・検証目的:
  ① 0 K 構造最適化を行わない未緩和初期構造から開始した場合に、発散せずに計算が回るか、
     各ステップの SCF 収束性・全エネルギー・温度 T の挙動がどう変化するか (初期熱ショックの有無と大きさ)
  ② 300 K の MD 中における最表面原子の Z 座標の最大変位 (振幅) とスラブ間ギャップがどう推移し、
     真空層 3.0 Å (ギャップ 6.0 Å) で隣接スラブとぶつからないか
==============================================================================
"""

import os
import sys
import re
import csv
import json
import time
import shutil
import datetime
import subprocess
import numpy as np

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache_sic"
os.makedirs("/tmp/matplotlib_cache_sic", exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
ENV_PREFIX = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
TEMPLATE_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_8periods_vac5A_natural_cleavage")
PREV_AIMD_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac3.0A_300K_100steps_rtx5080")
UNRELAXED_AIMD_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080")

LOG_FILE = os.path.join(WORKSPACE_DIR, "aimd_8periods_vac3.0A_unrelaxed_run.log")


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def create_unrelaxed_vac3A_data(src_unrelaxed_5A_path, dst_unrelaxed_3A_path):
    """
    未緩和の8周期・真空5.0Åスラブ (slab_10-10_288atoms_vac5A.data) から
    真空層部分のみを 5.0 Å → 3.0 Å に詰めた未緩和 LAMMPS データファイルを生成する。
    ・セル高さ Lz: 29.53540130124298 Å → 25.53540130124298 Å (-4.0 Å)
    ・全原子の z 座標: z → z - 2.0 Å (z_min = 3.0000 Å, z_max = 22.53540130124298 Å)
    ・初期スラブ間ギャップ: 6.0000 Å (完全未緩和の理想へき開切断構造)
    """
    with open(src_unrelaxed_5A_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out_lines = []
    in_atoms = False
    atoms_list = []
    zhi = 25.53540130124298

    for line in lines:
        stripped = line.strip()
        if "zlo zhi" in stripped:
            parts = stripped.split()
            zlo = float(parts[0])
            zhi = float(parts[1]) - 4.0  # 29.53540130124298 -> 25.53540130124298
            out_lines.append(f"{zlo:.1f} {zhi:.14f} zlo zhi\n")
            continue

        if stripped.startswith("Atoms"):
            in_atoms = True
            out_lines.append("Atoms # atomic\n\n")
            continue

        if in_atoms:
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) >= 5 and parts[0].isdigit():
                aid = int(parts[0])
                atype = int(parts[1])
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4]) - 2.0  # Shift z by -2.0 Å (bottom vac 5.0 -> 3.0 Å)
                atoms_list.append((aid, atype, x, y, z))
            continue

        out_lines.append(line)

    atoms_list.sort(key=lambda item: item[0])
    for aid, atype, x, y, z in atoms_list:
        out_lines.append(f"{aid:6d} {atype:3d} {x:20.14f} {y:20.14f} {z:20.14f}\n")

    with open(dst_unrelaxed_3A_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    z_arr = np.array([item[4] for item in atoms_list])
    log(
        f"Created unrelaxed initial structure {os.path.basename(dst_unrelaxed_3A_path)}: "
        f"{len(atoms_list)} atoms, z_min={z_arr.min():.4f} Å, z_max={z_arr.max():.4f} Å, Lz={zhi:.6f} Å "
        f"(initial inter-slab gap = {(z_arr.min() + zhi) - z_arr.max():.4f} Å)"
    )


def prepare_and_run_unrelaxed_aimd():
    log("==============================================================================")
    log("Starting 300 K NVT AIMD (100 steps = 100 fs) from UNRELAXED 8-period Vac 3.0 Å Slab")
    log("==============================================================================")

    os.makedirs(UNRELAXED_AIMD_DIR, exist_ok=True)

    # Copy common assets and identical QE-MDI engine from PREV_AIMD_DIR
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
        src = os.path.join(PREV_AIMD_DIR, asset)
        dst = os.path.join(UNRELAXED_AIMD_DIR, asset)
        shutil.copyfile(src, dst)
        if asset.endswith(".py"):
            os.chmod(dst, 0o755)

    # Create unrelaxed initial structure (8 periods, vac 3.0 Å)
    src_unrelaxed_5A = os.path.join(TEMPLATE_DIR, "slab_10-10_288atoms_vac5A.data")
    dst_unrelaxed_3A = os.path.join(UNRELAXED_AIMD_DIR, "slab_10-10_288atoms_vac3.0A_unrelaxed.data")
    create_unrelaxed_vac3A_data(src_unrelaxed_5A, dst_unrelaxed_3A)

    # Remove any old ./tmp so Step 0 starts cleanly from scratch for the unrelaxed geometry,
    # and Steps 1..100 use startingpot='file' and startingwfc='file'
    tmp_dir = os.path.join(UNRELAXED_AIMD_DIR, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    # Write in.lammps (100% identical to previous AIMD except read_data points to unrelaxed.data)
    in_lammps_content = """# ==============================================================================
# 2H-SiC {10-10} 8周期 (16層, 288原子) スラブモデル (真空層 各3.0Å, ギャップ 6.0Å)
# 【構造最適化なし (未緩和初期構造)】からの 300K NVT 第一原理分子動力学 (100 steps = 100 fs)
# ==============================================================================
# 単位系: metal (距離: Å, 時間: ps, エネルギー: eV, 温度: K, 質量: g/mol)
units           metal
dimension       3
boundary        p p p
atom_style      atomic
atom_modify     map yes

# 1. 初期構造の読み込み (8周期・真空3.0Å の 0K 構造最適化を行っていない理想切断スラブ構造)
read_data       slab_10-10_288atoms_vac3.0A_unrelaxed.data

# 原子質量設定 (Rule 2: Type 1: C = 12.011, Type 2: Si = 28.085)
mass            1 12.011
mass            2 28.085

pair_style      none

# 2. MDI 通信設定 (Quantum ESPRESSO を第一原理 QM エンジンとして連成)
fix             1 all mdi/qm elements C Si

# 3. 初期熱運動速度の付与 (Maxwell-Boltzmann 分布 @ 300K, 同一乱数シード 87654)
velocity        all create 300.0 87654 mom yes rot yes dist gaussian

# 4. 運動方程式の数値積分 & サーモスタット設定 (NVT アンサンブル @ 300K)
timestep        0.001
fix             2 all nvt temp 300.0 300.0 0.1

# 5. スラブ特有の重心ドリフト防止 (50ステップごとに全並進運動量をゼロにリセット)
fix             3 all momentum 50 linear 1 1 1

# 6. 出力設定 & ログ記録
thermo_style    custom step temp epair emol ke pe etotal press fmax fnorm
thermo          1
thermo_modify   flush yes

dump            1 all custom 1 dump.lammpstrj id type x y z vx vy vz fx fy fz
dump_modify     1 sort id flush yes

# 7. AIMD 実行 (100 steps = 100 fs = 0.1 ps)
run             100

write_data      slab_10-10_288atoms_vac3.0A_unrelaxed_aimd_100steps_final.data
undump          1
"""
    with open(os.path.join(UNRELAXED_AIMD_DIR, "in.lammps"), "w", encoding="utf-8") as f:
        f.write(in_lammps_content)

    for fn in ["dump.lammpstrj", "log.lammps", "lmp.log", "qe_engine.log", "espresso.pwo", "espresso_all_steps.pwo"]:
        p = os.path.join(UNRELAXED_AIMD_DIR, fn)
        if os.path.exists(p):
            os.remove(p)

    port = 8040
    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["QE_MPI_NP"] = "12"
    env["QE_OMP_THREADS"] = "2"

    lmp_bin = os.path.join(ENV_PREFIX, "bin", "lmp")
    py_bin = os.path.join(ENV_PREFIX, "bin", "python3")

    t0 = time.time()
    lmp_log_f = open(os.path.join(UNRELAXED_AIMD_DIR, "lmp.log"), "w")
    qe_log_f = open(os.path.join(UNRELAXED_AIMD_DIR, "qe_engine.log"), "w")

    lmp_proc = subprocess.Popen(
        [lmp_bin, "-mdi", f"-role DRIVER -name LAMMPS -method TCP -port {port}", "-in", "in.lammps", "-log", "log.lammps"],
        cwd=UNRELAXED_AIMD_DIR,
        env=env,
        stdout=lmp_log_f,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    qe_proc = subprocess.Popen(
        [py_bin, "qe_mdi_engine_rtx5080.py", "-mdi", f"-role ENGINE -name QE -method TCP -port {port} -hostname localhost"],
        cwd=UNRELAXED_AIMD_DIR,
        env=env,
        stdout=qe_log_f,
        stderr=subprocess.STDOUT,
    )

    lmp_proc.wait()
    try:
        qe_proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        qe_proc.kill()

    lmp_log_f.close()
    qe_log_f.close()
    elapsed = time.time() - t0

    # Winmostar 用アニメーション生成 & 3種推移グラフ自動生成
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=UNRELAXED_AIMD_DIR, env=env, check=False)
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_nvt_animation.xyz"], cwd=UNRELAXED_AIMD_DIR, env=env, check=False)
    subprocess.run([py_bin, "auto_generate_progression_graphs.py"], cwd=UNRELAXED_AIMD_DIR, env=env, check=False)

    log(f"Unrelaxed 300 K AIMD (100 steps) Completed in {elapsed:.1f}s ({elapsed/60.0:.1f} min)!")


def analyze_and_plot_results():
    Lz = 25.53540130124298
    thermo_data = {}
    with open(os.path.join(UNRELAXED_AIMD_DIR, "log.lammps")) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 10 and parts[0].isdigit():
                step = int(parts[0])
                thermo_data[step] = {
                    "temp": float(parts[1]),
                    "ke": float(parts[4]),
                    "pe": float(parts[5]),
                    "etotal": float(parts[6]),
                    "press": float(parts[7]),
                    "fmax": float(parts[8]),
                    "fnorm": float(parts[9]),
                }

    scf_data = {}
    with open(os.path.join(UNRELAXED_AIMD_DIR, "qe_engine.log")) as f:
        for line in f:
            m = re.search(r"\[Step (\d+)\] Done in ([\d\.]+)s \((\d+) SCF iters\)", line)
            if m:
                scf_data[int(m.group(1))] = (float(m.group(2)), int(m.group(3)))

    with open(os.path.join(UNRELAXED_AIMD_DIR, "dump.lammpstrj")) as f:
        lines = f.readlines()

    frames = []
    i = 0
    while i < len(lines):
        if "ITEM: TIMESTEP" in lines[i]:
            step = int(lines[i + 1].strip())
            natoms = int(lines[i + 3].strip())
            data = []
            for l in lines[i + 9 : i + 9 + natoms]:
                parts = l.split()
                data.append([int(parts[0]), int(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), float(parts[7])])
            data.sort(key=lambda x: x[0])
            frames.append((step, np.array(data)))
            i += 9 + natoms
        else:
            i += 1

    z0 = frames[0][1][:, 4]
    top_mask = z0 > 21.5
    bot_mask = z0 < 4.0
    surf_mask = top_mask | bot_mask

    rows = []
    for step, arr in frames:
        z = arr[:, 4]
        vz = arr[:, 5] * 0.001  # A/fs
        dz = z - z0
        dz_surf = dz[surf_mask]
        dz_top = dz[top_mask]
        dz_bot = dz[bot_mask]
        z_min = float(z.min())
        z_max = float(z.max())
        gap = (z_min + Lz) - z_max
        th = thermo_data.get(step, {})
        scf_t, scf_it = scf_data.get(step, (0.0, 0))
        rows.append({
            "step": step,
            "time_fs": float(step),
            "scf_iters": scf_it,
            "scf_time_s": scf_t,
            "temp_K": th.get("temp", 0.0),
            "ke_eV": th.get("ke", 0.0),
            "pe_eV": th.get("pe", 0.0),
            "etotal_eV": th.get("etotal", 0.0),
            "fmax_eV_A": th.get("fmax", 0.0),
            "z_min_A": round(z_min, 5),
            "z_max_A": round(z_max, 5),
            "gap_A": round(gap, 5),
            "dz_max_surf_A": round(float(np.max(np.abs(dz_surf))), 5),
            "dz_rms_surf_A": round(float(np.sqrt(np.mean(dz_surf**2))), 5),
            "dz_top_outward_max_A": round(float(np.max(dz_top)), 5),
            "dz_bot_outward_max_A": round(float(np.max(-dz_bot)), 5),
            "vz_max_surf_A_fs": round(float(np.max(np.abs(vz[surf_mask]))), 6),
        })

    csv_path = os.path.join(UNRELAXED_AIMD_DIR, "aimd_unrelaxed_100steps_summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    t = [r["time_fs"] for r in rows]
    temp = [r["temp_K"] for r in rows]
    etot = [r["etotal_eV"] for r in rows]
    pe = [r["pe_eV"] for r in rows]
    gap = [r["gap_A"] for r in rows]
    dz_max = [r["dz_max_surf_A"] for r in rows]
    dz_rms = [r["dz_rms_surf_A"] for r in rows]

    mincho_path = os.path.join(UNRELAXED_AIMD_DIR, "msmincho.ttc")
    prop_jp = fm.FontProperties(fname=mincho_path, size=11) if os.path.exists(mincho_path) else None

    # Plot 1: Surface Displacement & Gap
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.0, 5.2), dpi=300, sharex=True)
    ax1.plot(t, dz_max, color="#8A2BE2", lw=1.6, label="最大変位 |Δz|_max (最表面原子)")
    ax1.plot(t, dz_rms, color="#1E90FF", lw=1.6, ls="--", label="二乗平均変位 Δz_rms (最表面36原子)")
    ax1.set_ylabel("表面原子 Z方向変位 [Å]", fontproperties=prop_jp)
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.tick_params(direction="in", top=True, right=True)
    if prop_jp:
        ax1.legend(prop=prop_jp, loc="upper left", frameon=True)

    ax2.plot(t, gap, color="#2E8B57", lw=1.8, label="スラブ間ギャップ d_gap")
    ax2.axhline(6.0, color="#666666", ls=":", lw=1.0, label="初期ギャップ (6.00 Å)")
    ax2.set_xlabel("時間 [fs]", fontproperties=prop_jp)
    ax2.set_ylabel("スラブ間ギャップ [Å]", fontproperties=prop_jp)
    ax2.set_xlim(0, 100)
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.tick_params(direction="in", top=True, right=True)
    if prop_jp:
        ax2.legend(prop=prop_jp, loc="lower left", frameon=True)

    plt.tight_layout()
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(UNRELAXED_AIMD_DIR, f"AIMD_Surface_Displacement_and_Gap_100steps.{ext}"), dpi=300)
    plt.close(fig)

    # Plot 2: Temperature and Total Energy
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.0, 5.2), dpi=300, sharex=True)
    ax1.plot(t, temp, color="#D2691E", lw=1.6)
    ax1.axhline(300.0, color="#222222", ls="--", lw=1.0)
    ax1.set_ylabel("温度 T [K]", fontproperties=prop_jp)
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.tick_params(direction="in", top=True, right=True)

    ax2.plot(t, etot, color="#8A2BE2", lw=1.6, label="全エネルギー (TotEng = PE + KE)")
    ax2.plot(t, pe, color="#4682B4", lw=1.3, ls="--", label="ポテンシャルエネルギー (PotEng)")
    ax2.set_xlabel("時間 [fs]", fontproperties=prop_jp)
    ax2.set_ylabel("エネルギー [eV]", fontproperties=prop_jp)
    ax2.set_xlim(0, 100)
    ax2.ticklabel_format(useOffset=False, style="plain", axis="y")
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.tick_params(direction="in", top=True, right=True)
    if prop_jp:
        ax2.legend(prop=prop_jp, loc="best", frameon=True)

    plt.tight_layout()
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(UNRELAXED_AIMD_DIR, f"AIMD_Temperature_and_Energy_100steps.{ext}"), dpi=300)
    plt.close(fig)

    log("Generated summary CSV and AIMD analysis plots for unrelaxed initial structure.")


if __name__ == "__main__":
    try:
        prepare_and_run_unrelaxed_aimd()
        analyze_and_plot_results()
        log("ALL UNRELAXED AIMD STEPS COMPLETED SUCCESSFULLY!")
    except Exception as exc:
        log(f"FATAL ERROR: {exc}")
        raise

