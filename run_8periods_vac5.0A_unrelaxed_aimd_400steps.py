#!/usr/bin/env python3
r"""
run_8periods_vac5.0A_unrelaxed_aimd_400steps.py
==============================================================================
2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 5.0 Å (上下各 5.0 Å, スラブ間ギャップ 10.0 Å)
【構造最適化なし (未緩和スラブモデル)】からの 300 K NVT 第一原理分子動力学 (AIMD 400 steps = 400 fs = 0.4 ps)

・計算条件:
  真空層の厚さ (3.0 Å -> 5.0 Å, セル高さ Lz = 29.53540130124298 Å, 初期ギャップ 10.0 Å) 以外は、
  先ほどの 8周期・真空3.0Å・構造最適化なしスラブモデルの 400 ステップ AIMD と 100% 同一条件。
・保存先 (既存データ非上書き・新規ディレクトリ作成):
  - ローカル: aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080/
  - NAS (計算データ): \\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法\{101_0}８周期5.0Å
  - NAS (実行コード): \\192.168.12.69\Results\yamazaki\research\実行コード\{101_0}8周期5.0Å　構造最適化なし
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
import matplotlib.ticker as ticker

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
ENV_PREFIX = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
TEMPLATE_5A_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_8periods_vac5A_natural_cleavage")
PREV_SLAB3A_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080")
SLAB5A_400_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080")

LOG_FILE = os.path.join(WORKSPACE_DIR, "aimd_8periods_vac5.0A_unrelaxed_400steps_run.log")


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sync_to_nas():
    pass


def prepare_slab_vac5A_400_aimd():
    log("==============================================================================")
    log("Preparing 300 K NVT AIMD (400 steps = 400 fs) from UNRELAXED 8-period Vac 5.0 Å Slab")
    log("(Initial inter-slab gap = 10.0 Å, Lz = 29.53540130124298 Å, 288 atoms)")
    log("==============================================================================")

    os.makedirs(SLAB5A_400_DIR, exist_ok=True)

    # Copy common assets and identical QE-MDI engine from PREV_SLAB3A_DIR
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
        src = os.path.join(PREV_SLAB3A_DIR, asset)
        dst = os.path.join(SLAB5A_400_DIR, asset)
        shutil.copyfile(src, dst)
        if asset.endswith(".py"):
            os.chmod(dst, 0o755)

    # Copy unrelaxed 8-period Vac 5.0 Å initial structure (z_min=5.0 Å, z_max=24.5354 Å, Lz=29.5354 Å, gap=10.0 Å)
    src_unrelaxed_5A = os.path.join(TEMPLATE_5A_DIR, "slab_10-10_288atoms_vac5A.data")
    dst_unrelaxed_5A = os.path.join(SLAB5A_400_DIR, "slab_10-10_288atoms_vac5.0A_unrelaxed.data")
    shutil.copyfile(src_unrelaxed_5A, dst_unrelaxed_5A)
    for ext in ["cif", "xyz"]:
        s_f = os.path.join(TEMPLATE_5A_DIR, f"slab_10-10_288atoms_vac5A.{ext}")
        if os.path.exists(s_f):
            shutil.copyfile(s_f, os.path.join(SLAB5A_400_DIR, f"slab_10-10_288atoms_vac5.0A_unrelaxed.{ext}"))

    # Clean ./tmp so Step 0 starts cleanly from scratch for the Vac 5.0 Å unrelaxed geometry,
    # and Steps 1..400 reuse ./tmp/pwscf.save (wfc1.hdf5 & charge-density.hdf5) via startingpot/wfc='file'
    tmp_dir = os.path.join(SLAB5A_400_DIR, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    # Write in.lammps (100% identical to Vac 3.0 Å AIMD except read_data points to vac5.0A_unrelaxed.data and total run is 400 steps)
    in_lammps_content = """# ==============================================================================
# 2H-SiC {10-10} 8周期 (16層, 288原子) スラブモデル (真空層 各5.0Å, ギャップ 10.0Å)
# 【構造最適化なし (未緩和初期構造)】からの 300K NVT 第一原理分子動力学 (400 steps = 400 fs = 0.4 ps)
# ==============================================================================
# 単位系: metal (距離: Å, 時間: ps, エネルギー: eV, 温度: K, 質量: g/mol)
units           metal
dimension       3
boundary        p p p
atom_style      atomic
atom_modify     map yes

# 1. 初期構造の読み込み (8周期・真空5.0Å の 0K 構造最適化を行っていない理想切断スラブ構造)
read_data       slab_10-10_288atoms_vac5.0A_unrelaxed.data

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

# 7. 定期リスタート出力 & AIMD 実行 (400 steps = 400 fs = 0.4 ps)
restart         50 restart.slab_vac5.0A_unrelaxed_step
run             400

write_restart   restart.slab_vac5.0A_unrelaxed_400steps_final
write_data      slab_10-10_288atoms_vac5.0A_unrelaxed_aimd_400steps_final.data
undump          1
"""
    with open(os.path.join(SLAB5A_400_DIR, "in.lammps"), "w", encoding="utf-8") as f:
        f.write(in_lammps_content)

    for fn in ["dump.lammpstrj", "log.lammps", "lmp.log", "qe_engine.log", "espresso.pwo", "espresso_all_steps.pwo"]:
        p = os.path.join(SLAB5A_400_DIR, fn)
        if os.path.exists(p):
            os.remove(p)

    log("Prepared unrelaxed Vac 5.0 Å slab 400-step AIMD directory and input files.")
    sync_to_nas()


def run_slab_vac5A_400_aimd():
    port = 8052
    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["QE_MPI_NP"] = "12"
    env["QE_OMP_THREADS"] = "2"

    lmp_bin = os.path.join(ENV_PREFIX, "bin", "lmp")
    py_bin = os.path.join(ENV_PREFIX, "bin", "python3")

    t0 = time.time()
    lmp_log_f = open(os.path.join(SLAB5A_400_DIR, "lmp.log"), "w")
    qe_log_f = open(os.path.join(SLAB5A_400_DIR, "qe_engine.log"), "w")

    log(f"Launching LAMMPS driver and QE-MDI engine on port {port} (Step 0..400 live SCF for Vac 5.0 Å unrelaxed slab)...")
    lmp_proc = subprocess.Popen(
        [lmp_bin, "-mdi", f"-role DRIVER -name LAMMPS -method TCP -port {port}", "-in", "in.lammps", "-log", "log.lammps"],
        cwd=SLAB5A_400_DIR,
        env=env,
        stdout=lmp_log_f,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    qe_proc = subprocess.Popen(
        [py_bin, "qe_mdi_engine_rtx5080.py", "-mdi", f"-role ENGINE -name QE -method TCP -port {port} -hostname localhost"],
        cwd=SLAB5A_400_DIR,
        env=env,
        stdout=qe_log_f,
        stderr=subprocess.STDOUT,
    )

    last_sync_time = time.time()
    while lmp_proc.poll() is None:
        time.sleep(15)
        if time.time() - last_sync_time >= 300:
            dump_path = os.path.join(SLAB5A_400_DIR, "dump.lammpstrj")
            if os.path.exists(dump_path) and os.path.getsize(dump_path) > 0:
                subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=SLAB5A_400_DIR, env=env, check=False)
            sync_to_nas()
            last_sync_time = time.time()

    try:
        qe_proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        qe_proc.kill()

    lmp_log_f.close()
    qe_log_f.close()
    elapsed = time.time() - t0

    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=SLAB5A_400_DIR, env=env, check=False)
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_nvt_animation.xyz"], cwd=SLAB5A_400_DIR, env=env, check=False)
    subprocess.run([py_bin, "auto_generate_progression_graphs.py"], cwd=SLAB5A_400_DIR, env=env, check=False)

    log(f"Unrelaxed Vac 5.0 Å Slab 300 K AIMD (400 steps) Completed in {elapsed:.1f}s ({elapsed/60.0:.1f} min)!")


def analyze_and_plot_results():
    Lz = 29.535401301242981
    thermo_data = {}
    with open(os.path.join(SLAB5A_400_DIR, "log.lammps")) as f:
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
    with open(os.path.join(SLAB5A_400_DIR, "qe_engine.log")) as f:
        for line in f:
            m = re.search(r"\[Step (\d+)\] Done in ([\d\.]+)s \((\d+) SCF iters\)", line)
            if m:
                scf_data[int(m.group(1))] = (float(m.group(2)), int(m.group(3)))

    with open(os.path.join(SLAB5A_400_DIR, "dump.lammpstrj")) as f:
        lines = f.readlines()

    frames_dict = {}
    i = 0
    while i < len(lines):
        if "ITEM: TIMESTEP" in lines[i]:
            step = int(lines[i + 1].strip())
            natoms = int(lines[i + 3].strip())
            data = []
            for l in lines[i + 9 : i + 9 + natoms]:
                parts = l.split()
                data.append([
                    int(parts[0]),
                    int(parts[1]),
                    float(parts[2]),
                    float(parts[3]),
                    float(parts[4]),
                    float(parts[5]),
                    float(parts[6]),
                    float(parts[7]),
                ])
            data.sort(key=lambda x: x[0])
            frames_dict[step] = np.array(data)
            i += 9 + natoms
        else:
            i += 1

    sorted_steps = sorted(frames_dict.keys())
    z0 = frames_dict[0][:, 4]
    top_mask = z0 > 23.5
    bot_mask = z0 < 6.0
    surf_mask = top_mask | bot_mask

    rows = []
    for step in sorted_steps:
        arr = frames_dict[step]
        z = arr[:, 4]
        vz = arr[:, 7] * 0.001  # A/fs
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
            "press_bar": th.get("press", 0.0),
            "fmax_eV_A": th.get("fmax", 0.0),
            "fnorm_eV_A": th.get("fnorm", 0.0),
            "z_min_A": round(z_min, 5),
            "z_max_A": round(z_max, 5),
            "gap_A": round(gap, 5),
            "dz_max_surf_A": round(float(np.max(np.abs(dz_surf))), 5),
            "dz_rms_surf_A": round(float(np.sqrt(np.mean(dz_surf**2))), 5),
            "dz_top_outward_max_A": round(float(np.max(dz_top)), 5),
            "dz_bot_outward_max_A": round(float(np.max(-dz_bot)), 5),
            "vz_max_surf_A_fs": round(float(np.max(np.abs(vz[surf_mask]))), 6),
        })

    csv_path = os.path.join(SLAB5A_400_DIR, "aimd_unrelaxed_vac5.0A_400steps_summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    def calc_window_stats(start_step, end_step=None):
        sub = [r for r in rows if r["step"] >= start_step and (end_step is None or r["step"] <= end_step)]
        t_arr = np.array([r["temp_K"] for r in sub])
        et_arr = np.array([r["etotal_eV"] for r in sub])
        pe_arr = np.array([r["pe_eV"] for r in sub])
        ke_arr = np.array([r["ke_eV"] for r in sub])
        gap_arr = np.array([r["gap_A"] for r in sub])
        dz_arr = np.array([r["dz_max_surf_A"] for r in sub])
        return {
            "window": f"Step {start_step}..{sub[-1]['step']} ({len(sub)} points)",
            "temp_mean_K": float(np.mean(t_arr)),
            "temp_std_K": float(np.std(t_arr)),
            "etotal_mean_eV": float(np.mean(et_arr)),
            "etotal_std_eV": float(np.std(et_arr)),
            "pe_mean_eV": float(np.mean(pe_arr)),
            "pe_std_eV": float(np.std(pe_arr)),
            "ke_mean_eV": float(np.mean(ke_arr)),
            "ke_std_eV": float(np.std(ke_arr)),
            "gap_mean_A": float(np.mean(gap_arr)),
            "gap_min_A": float(np.min(gap_arr)),
            "dz_surf_max_A": float(np.max(dz_arr)),
        }

    stats = {
        "natoms": 288,
        "n_periods": 8,
        "vacuum_A": 5.0,
        "initial_gap_A": 10.0,
        "target_temp_K": 300.0,
        "total_steps": rows[-1]["step"],
        "slab_0K_relaxed_energy_eV": -127685.1583,
        "slab_0K_unrelaxed_energy_eV": float(rows[0]["pe_eV"]),
        "bulk_300K_equil_pe_eV": -127714.79,
        "ensemble_all_0_to_400": calc_window_stats(0),
        "ensemble_phase1_0_to_100": calc_window_stats(0, 100),
        "ensemble_phase2_100_to_400": calc_window_stats(100),
        "ensemble_equil_200_to_400": calc_window_stats(200),
        "ensemble_equil_300_to_400": calc_window_stats(300),
    }
    with open(os.path.join(SLAB5A_400_DIR, "aimd_unrelaxed_vac5.0A_400steps_ensemble_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

    plt.rcParams["mathtext.fontset"] = "stix"
    mincho_path = os.path.join(SLAB5A_400_DIR, "msmincho.ttc")
    times_path = os.path.join(SLAB5A_400_DIR, "times.ttf")
    prop_label = fm.FontProperties(fname=mincho_path, size=10.5) if os.path.exists(mincho_path) else fm.FontProperties(size=10.5)
    prop_tick = fm.FontProperties(fname=times_path, size=9.5) if os.path.exists(times_path) else fm.FontProperties(size=9.5)
    prop_legend = fm.FontProperties(fname=mincho_path, size=8.5) if os.path.exists(mincho_path) else fm.FontProperties(size=8.5)

    steps = np.array([r["step"] for r in rows])
    temp = np.array([r["temp_K"] for r in rows])
    etot = np.array([r["etotal_eV"] for r in rows])
    pe = np.array([r["pe_eV"] for r in rows])
    ke = np.array([r["ke_eV"] for r in rows])
    gap = np.array([r["gap_A"] for r in rows])
    dz_max = np.array([r["dz_max_surf_A"] for r in rows])
    dz_rms = np.array([r["dz_rms_surf_A"] for r in rows])

    fig_w = 8.0 / 2.54
    fig_h = 6.2 / 2.54
    mark_every = 15

    def style_ax(ax, xlabel, ylabel):
        ax.set_xlabel(xlabel, fontproperties=prop_label, labelpad=4)
        ax.set_ylabel(ylabel, fontproperties=prop_label, labelpad=4)
        ax.tick_params(direction="in", top=True, right=True, length=3.5, width=0.8)
        for sp in ax.spines.values():
            sp.set_linewidth(0.9)
        ax.set_xlim(-10, 410)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax.yaxis.get_major_formatter().set_useOffset(False)
        ax.yaxis.get_major_formatter().set_scientific(False)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_fontproperties(prop_tick)

    # 1. 全エネルギー推移 (Word 8cm)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.plot(steps, etot, color="#8A2BE2", lw=1.1, zorder=2)
    ax.scatter(steps[::mark_every], etot[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0, zorder=3)
    style_ax(ax, "MDステップ [step]", r"全エネルギー [$\mathrm{eV}$]")
    e_min, e_max = float(np.min(etot)), float(np.max(etot))
    span = max(e_max - e_min, 0.2)
    ax.set_ylim(e_min - 0.35 * span, e_max + 0.35 * span)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"全エネルギー推移_未緩和5.0A_AIMD_400steps_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 2. ポテンシャルエネルギー推移 (Word 8cm)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.plot(steps, pe, color="#8A2BE2", lw=1.1, zorder=2)
    ax.scatter(steps[::mark_every], pe[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0, zorder=3)
    style_ax(ax, "MDステップ [step]", r"ポテンシャルエネルギー [$\mathrm{eV}$]")
    p_min, p_max = float(np.min(pe)), float(np.max(pe))
    pspan = max(p_max - p_min, 1.0)
    ax.set_ylim(p_min - 0.15 * pspan, p_max + 0.15 * pspan)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"ポテンシャルエネルギー推移_未緩和5.0A_AIMD_400steps_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 3. エネルギー変化量推移 (Word 8cm)
    d_etot = etot - etot[0]
    d_pe = pe - pe[0]
    d_ke = ke - ke[0]
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.axhline(0.0, color="#888888", ls=":", lw=0.8, zorder=1)
    ax.plot(steps, d_etot, color="#8A2BE2", lw=1.2, label=r"全エネルギー $\Delta E_{\mathrm{tot}}$", zorder=4)
    ax.scatter(steps[::mark_every], d_etot[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=24, linewidths=0.9, zorder=5)
    ax.plot(steps, d_pe, color="#1E90FF", lw=1.1, ls="--", label=r"ポテンシャル $\Delta E_{\mathrm{pot}}$", zorder=3)
    ax.plot(steps, d_ke, color="#D2691E", lw=1.1, ls="-.", label=r"運動エネルギー $\Delta E_{\mathrm{kin}}$", zorder=3)
    style_ax(ax, "MDステップ [step]", r"初期値からのエネルギー変化 [$\mathrm{eV}$]")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    ax.legend(prop=prop_legend, loc="best", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"エネルギー変化量推移_未緩和5.0A_AIMD_400steps_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 4. 温度推移 (Word 8cm)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.axhline(300.0, color="#222222", ls="--", lw=1.0, zorder=1)
    ax.plot(steps, temp, color="#8A2BE2", lw=1.1, zorder=2)
    ax.scatter(steps[::mark_every], temp[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0, zorder=3)
    style_ax(ax, "MDステップ [step]", r"温度 [$\mathrm{K}$]")
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"温度推移_未緩和5.0A_AIMD_400steps_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 5. 表面原子変位 & スラブ間ギャップ推移
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.2, 5.4), dpi=300, sharex=True)
    ax1.plot(steps, dz_max, color="#8A2BE2", lw=1.5, label=r"最大変位 $|\Delta z|_{\max}$ (最表面原子)")
    ax1.plot(steps, dz_rms, color="#1E90FF", lw=1.5, ls="--", label=r"二乗平均変位 $\Delta z_{\mathrm{rms}}$ (最表面36原子)")
    ax1.set_ylabel(r"表面原子 Z方向変位 [$\mathrm{\AA}$]", fontproperties=prop_label)
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.tick_params(direction="in", top=True, right=True)
    ax1.legend(prop=prop_legend, loc="upper left", frameon=True)

    ax2.plot(steps, gap, color="#2E8B57", lw=1.6, label=r"スラブ間ギャップ $d_{\mathrm{gap}}$")
    ax2.axhline(10.0, color="#666666", ls="--", lw=1.0, label="初期ギャップ (10.00 Å)")
    ax2.set_xlabel(r"時間 / MDステップ [$\mathrm{fs}$]", fontproperties=prop_label)
    ax2.set_ylabel(r"スラブ間ギャップ [$\mathrm{\AA}$]", fontproperties=prop_label)
    ax2.set_xlim(-10, 410)
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.tick_params(direction="in", top=True, right=True)
    ax2.legend(prop=prop_legend, loc="lower left", frameon=True)

    for a in (ax1, ax2):
        for lbl in a.get_xticklabels() + a.get_yticklabels():
            lbl.set_fontproperties(prop_tick)

    fig.tight_layout(pad=0.5)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"AIMD_Surface_Displacement_and_Gap_vac5.0A_400steps.{ext}"), dpi=300)
    plt.close(fig)

    # 6. エネルギー・温度総合推移 (プレゼン仕様)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6.5, 7.2), dpi=300, sharex=True)
    ax1.plot(steps, temp, color="#D2691E", lw=1.5, label=r"温度 $T$ (未緩和スラブ 真空5.0Å, 288原子)")
    ax1.axhline(300.0, color="#222222", ls="--", lw=1.0, label="目標温度 (300 K)")
    ax1.set_ylabel(r"温度 $T$ [$\mathrm{K}$]", fontproperties=prop_label)
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.tick_params(direction="in", top=True, right=True)
    ax1.legend(prop=prop_legend, loc="lower right", frameon=True)

    ax2.plot(steps, etot, color="#8A2BE2", lw=1.5, label=r"全エネルギー $E_{\mathrm{tot}} = E_{\mathrm{pot}} + E_{\mathrm{kin}}$")
    ax2.scatter(steps[::mark_every], etot[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0)
    ax2.set_ylabel(r"全エネルギー [$\mathrm{eV}$]", fontproperties=prop_label)
    ax2.yaxis.get_major_formatter().set_useOffset(False)
    ax2.yaxis.get_major_formatter().set_scientific(False)
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    ax2.set_ylim(e_min - 0.35 * span, e_max + 0.35 * span)
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.tick_params(direction="in", top=True, right=True)
    ax2.legend(prop=prop_legend, loc="upper left", frameon=True)

    ax3.plot(steps, pe, color="#1E90FF", lw=1.5, label=r"ポテンシャルエネルギー $E_{\mathrm{pot}}$")
    ax3.scatter(steps[::mark_every], pe[::mark_every], marker="o", facecolors="none", edgecolors="#1E90FF", s=24, linewidths=0.9)
    ax3.axhline(stats["ensemble_equil_200_to_400"]["pe_mean_eV"], color="#2E8B57", ls="--", lw=1.1,
                label=f"Step 200..400 平均 $\\langle E_{{\\mathrm{{pot}}}}\\rangle = {stats['ensemble_equil_200_to_400']['pe_mean_eV']:.2f}$ eV")
    ax3.set_xlabel(r"時間 / MDステップ [$\mathrm{fs}$]", fontproperties=prop_label)
    ax3.set_ylabel(r"ポテンシャル [$\mathrm{eV}$]", fontproperties=prop_label)
    ax3.yaxis.get_major_formatter().set_useOffset(False)
    ax3.yaxis.get_major_formatter().set_scientific(False)
    ax3.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    ax3.set_xlim(-10, 410)
    ax3.grid(True, ls=":", alpha=0.5)
    ax3.tick_params(direction="in", top=True, right=True)
    ax3.legend(prop=prop_legend, loc="lower right", frameon=True)

    for a in (ax1, ax2, ax3):
        for lbl in a.get_xticklabels() + a.get_yticklabels():
            lbl.set_fontproperties(prop_tick)

    fig.tight_layout(pad=0.5)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"エネルギー総合推移_未緩和5.0A_AIMD_400steps_プレゼン仕様.{ext}"), dpi=300)
        fig.savefig(os.path.join(SLAB5A_400_DIR, f"AIMD_Temperature_and_Energy_vac5.0A_400steps.{ext}"), dpi=300)
    plt.close(fig)

    log("Generated summary CSV, ensemble stats JSON, and unrelaxed Vac 5.0 Å slab 400-step AIMD plots.")
    sync_to_nas()


if __name__ == "__main__":
    try:
        prepare_slab_vac5A_400_aimd()
        run_slab_vac5A_400_aimd()
        analyze_and_plot_results()
        log("ALL UNRELAXED VAC 5.0 Å SLAB 400-STEP AIMD TASKS COMPLETED SUCCESSFULLY!")
    except Exception as exc:
        log(f"FATAL ERROR: {exc}")
        raise

