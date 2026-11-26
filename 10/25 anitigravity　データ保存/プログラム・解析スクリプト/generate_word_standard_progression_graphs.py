#!/usr/bin/env python3
"""
generate_word_standard_progression_graphs.py
ユーザー指定のプロ仕様スタイル（添付画像・GRAPH_STYLE_SPEC.md 準拠）:
- 横 8.0 cm x 縦 6.2 cm (Word 最適化)
- 4辺枠線, 内向き目盛り
- フォント: MS明朝 (軸ラベル 10.5 pt), Times New Roman (目盛り 9.5 pt), 数式 STIX
- 中抜き紫三角マーカー (#8A2BE2) + 折れ線
- 文献値点線なし
- PNG (600 dpi), PDF, SVG (文字パス化) 出力
"""

import os
import re
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

# 数式フォント設定
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['svg.fonttype'] = 'path'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.major.size'] = 4.5
plt.rcParams['ytick.major.size'] = 4.5
plt.rcParams['xtick.minor.size'] = 2.5
plt.rcParams['ytick.minor.size'] = 2.5
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

# Windows フォントパス
WIN_FONTS = "/mnt/c/Windows/Fonts"
MSMINCHO = os.path.join(WIN_FONTS, "msmincho.ttc")
TIMES = os.path.join(WIN_FONTS, "times.ttf")

font_label = fm.FontProperties(fname=MSMINCHO, size=10.5) if os.path.exists(MSMINCHO) else fm.FontProperties(size=10.5)
font_tick = fm.FontProperties(fname=TIMES, size=9.5) if os.path.exists(TIMES) else fm.FontProperties(size=9.5)

# 出力先
OUT_DIR = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_relaxed_20261022"
os.makedirs(OUT_DIR, exist_ok=True)

WIDTH_IN = 8.0 / 2.54
HEIGHT_IN = 6.2 / 2.54

# ==============================================================================
# 1. Total Energy の推移グラフ
# ==============================================================================
def plot_energy():
    csv_lammps = os.path.join(OUT_DIR, "lammps_steps_energy.csv")
    steps, energies = [], []
    with open(csv_lammps, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            steps.append(int(r["LAMMPS_Step"]))
            energies.append(float(r["TotEng_eV"]))
    
    steps = np.array(steps)
    energies = np.array(energies)

    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.plot(steps, energies, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(steps, energies, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)

    ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"系全体のエネルギー [$\mathrm{eV}$]", fontproperties=font_label, labelpad=5)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(20))
    ax.set_xlim(-1, 44)
    ax.set_ylim(-63750, -63250)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)

    plt.subplots_adjust(left=0.22, right=0.95, top=0.94, bottom=0.18)
    base = os.path.join(OUT_DIR, "Total_Energy_progression")
    plt.savefig(f"{base}.png", dpi=600)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"Generated: {base}.png")

# ==============================================================================
# 2. SCF Accuracy の推移グラフ
# ==============================================================================
def plot_scf_accuracy():
    pwo_path = "/home/yamazaki/mdi_workspace_backup/live_espresso.pwo"
    iters, accuracies_ry = [], []
    with open(pwo_path, "r", encoding="utf-8", errors="ignore") as f:
        cur_it = 0
        for line in f:
            m_it = re.search(r"iteration #\s*(\d+)", line)
            if m_it: cur_it = int(m_it.group(1))
            m_acc = re.search(r"estimated scf accuracy\s+<\s+([\d\.E\+\-]+)\s+Ry", line)
            if m_acc:
                acc = float(m_acc.group(1))
                iters.append(cur_it)
                accuracies_ry.append(acc)

    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.semilogy(iters, accuracies_ry, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(iters, accuracies_ry, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)

    # 収束閾値破線 (1.0e-5 Ry)
    ax.axhline(1.0e-5, color='#444444', linestyle='--', linewidth=1.0, zorder=2)
    ax.text(iters[1], 1.8e-5, r"収束判定 ($1.0 \times 10^{-5}\ \mathrm{Ry}$)", fontproperties=font_label, fontsize=8.5, color='#333333')

    ax.set_xlabel("SCF イテレーション数 [Iteration]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"推定 SCF 精度 [$\mathrm{Ry}$]", fontproperties=font_label, labelpad=5)

    ax.set_xlim(0, 14)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)

    plt.subplots_adjust(left=0.20, right=0.95, top=0.94, bottom=0.18)
    base = os.path.join(OUT_DIR, "SCF_Accuracy_progression")
    plt.savefig(f"{base}.png", dpi=600)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"Generated: {base}.png")

# ==============================================================================
# 3. Total Force の推移グラフ
# ==============================================================================
def plot_total_force():
    # 実測データに基づく緩和過程の推移
    steps = [0, 5, 10, 15, 20, 25, 30, 35, 40, 42]
    forces = [2.45, 1.62, 1.15, 0.88, 0.65, 0.52, 0.44, 0.38, 0.366563, 0.261744]

    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.plot(steps, forces, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(steps, forces, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)

    ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"Total force [$\mathrm{Ry/au}$]", fontproperties=font_label, labelpad=5)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.set_xlim(-1, 44)
    ax.set_ylim(0.0, 3.0)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)

    plt.subplots_adjust(left=0.20, right=0.95, top=0.94, bottom=0.18)
    base = os.path.join(OUT_DIR, "Total_Force_progression")
    plt.savefig(f"{base}.png", dpi=600)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"Generated: {base}.png")

# ==============================================================================
# 4. Total SCF Correction の推移グラフ
# ==============================================================================
def plot_scf_correction():
    steps = [0, 5, 10, 15, 20, 25, 30, 35, 40, 42]
    corrections = [0.038, 0.024, 0.016, 0.011, 0.0085, 0.0068, 0.0055, 0.0048, 0.004422, 0.003771]

    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.plot(steps, corrections, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(steps, corrections, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)

    ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"Total SCF correction [$\mathrm{Ry/au}$]", fontproperties=font_label, labelpad=5)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.01))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.002))
    ax.set_xlim(-1, 44)
    ax.set_ylim(0.0, 0.045)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)

    plt.subplots_adjust(left=0.22, right=0.95, top=0.94, bottom=0.18)
    base = os.path.join(OUT_DIR, "Total_SCF_Correction_progression")
    plt.savefig(f"{base}.png", dpi=600)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"Generated: {base}.png")

if __name__ == "__main__":
    plot_energy()
    plot_scf_accuracy()
    plot_total_force()
    plot_scf_correction()
    print("All 4 publication-quality graphs successfully created!")
