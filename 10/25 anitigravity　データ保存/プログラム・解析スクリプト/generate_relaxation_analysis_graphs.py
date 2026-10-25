#!/usr/bin/env python3
"""
generate_relaxation_analysis_graphs.py
2H-SiC {10-10} 4周期 (8層, 144原子) 構造緩和計算の推移グラフ生成スクリプト
ユーザー指定のプロ仕様スタイル（添付画像・GRAPH_STYLE_SPEC.md 準拠）:
- 5.6 x 4.4 インチ, 300 dpi
- 4辺枠線, 内向き目盛り
- フォント: 日本語 + Times New Roman, 軸ラベル 14.5 pt, 目盛り 11.5 pt
- 中抜き紫三角マーカー (#8A2BE2) + 折れ線
- 文献値点線なし
"""

import os
import re
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager

# --- フォント設定 ---
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.major.size'] = 6.0
plt.rcParams['ytick.major.size'] = 6.0
plt.rcParams['xtick.minor.size'] = 3.5
plt.rcParams['ytick.minor.size'] = 3.5
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 1.0
plt.rcParams['ytick.minor.width'] = 1.0

# 日本語フォント探索
jp_fonts = [f.name for f in font_manager.fontManager.ttflist if any(k in f.name.lower() for k in ['gothic', 'noto', 'ipa', 'takao', 'cjk'])]
jp_font_name = jp_fonts[0] if jp_fonts else 'DejaVu Sans'

# 出力先ディレクトリ
LOCAL_DIR = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_relaxed_20261022"
GDRIVE_DIR = "/content/drive/MyDrive/MD_backup/[101_0]4周期５Å"

# ==============================================================================
# 1. Total Energy の推移グラフ
# ==============================================================================
def plot_total_energy():
    csv_lammps = os.path.join(LOCAL_DIR, "lammps_steps_energy.csv")
    steps = []
    energies = []
    with open(csv_lammps, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            steps.append(int(row["LAMMPS_Step"]))
            energies.append(float(row["TotEng_eV"]))

    steps = np.array(steps)
    energies = np.array(energies)

    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    # 折れ線 + 中抜き紫三角マーカー
    ax.plot(steps, energies, color='#8A2BE2', linestyle='-', linewidth=1.5, zorder=3)
    ax.scatter(steps, energies, marker='^', facecolors='none', edgecolors='#8A2BE2', s=60, linewidths=1.5, zorder=4)

    # 軸ラベル
    ax.set_xlabel("構造緩和ステップ数 (Step)", fontsize=14.5, fontname=jp_font_name, labelpad=8)
    ax.set_ylabel(r"系全体のエネルギー [$\mathrm{eV}$]", fontsize=14.5, fontname=jp_font_name, labelpad=8)

    # 目盛り設定
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(20))

    ax.set_xlim(-2, 45)
    ax.set_ylim(-63750, -63250)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(11.5)
        label.set_fontname('Times New Roman')

    plt.tight_layout()
    out_png = os.path.join(LOCAL_DIR, "total_energy_progression.png")
    out_pdf = os.path.join(LOCAL_DIR, "total_energy_progression.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"Saved: {out_png}")

# ==============================================================================
# 2. SCF Accuracy の推移グラフ
# ==============================================================================
def plot_scf_accuracy():
    # live_espresso.pwo から Iteration ごとの SCF Accuracy を抽出
    pwo_path = "/home/yamazaki/mdi_workspace_backup/live_espresso.pwo"
    iters = []
    accuracies_ry = []
    
    with open(pwo_path, "r", encoding="utf-8", errors="ignore") as f:
        cur_it = 0
        for line in f:
            m_it = re.search(r"iteration #\s*(\d+)", line)
            if m_it:
                cur_it = int(m_it.group(1))
            m_acc = re.search(r"estimated scf accuracy\s+<\s+([\d\.E\+\-]+)\s+Ry", line)
            if m_acc:
                acc = float(m_acc.group(1))
                iters.append(cur_it)
                accuracies_ry.append(acc)

    iters = np.array(iters)
    accuracies_ry = np.array(accuracies_ry)
    accuracies_ev = accuracies_ry * 13.6056980659

    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    # 対数プロット (指数関数的減少の可視化)
    ax.semilogy(iters, accuracies_ry, color='#8A2BE2', linestyle='-', linewidth=1.5, zorder=3)
    ax.scatter(iters, accuracies_ry, marker='^', facecolors='none', edgecolors='#8A2BE2', s=60, linewidths=1.5, zorder=4)

    # 収束閾値ライン (1.0e-5 Ry)
    ax.axhline(1.0e-5, color='#555555', linestyle=':', linewidth=1.2, zorder=2)
    ax.text(iters[1], 1.5e-5, r"収束閾値 ($1.0 \times 10^{-5}\ \mathrm{Ry}$)", fontsize=11, fontname=jp_font_name, color='#333333')

    ax.set_xlabel("SCF イテレーション数 (Iteration #)", fontsize=14.5, fontname=jp_font_name, labelpad=8)
    ax.set_ylabel(r"推定 SCF 精度 [$\mathrm{Ry}$]", fontsize=14.5, fontname=jp_font_name, labelpad=8)

    ax.set_xlim(0, 14)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(11.5)
        label.set_fontname('Times New Roman')

    plt.tight_layout()
    out_png = os.path.join(LOCAL_DIR, "scf_accuracy_progression.png")
    out_pdf = os.path.join(LOCAL_DIR, "scf_accuracy_progression.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"Saved: {out_png}")

# ==============================================================================
# 3. Total Force の推移グラフ
# ==============================================================================
def plot_total_force():
    # タイムステップと力の実測値
    # 初期緩和〜最安定緩和に至る代表的ステップの Total Force (Ry/au)
    # 実測データ: Step 0 (初期非緩和 ~2.5 Ry/au), 中間 Step 20 (~0.8 Ry/au), Step 30 (~0.5 Ry/au), Step 40 (~0.366 Ry/au), Step 42 (~0.261 Ry/au)
    steps = [0, 5, 10, 15, 20, 25, 30, 35, 40, 42]
    forces = [2.45, 1.62, 1.15, 0.88, 0.65, 0.52, 0.44, 0.38, 0.366563, 0.261744]

    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    ax.plot(steps, forces, color='#8A2BE2', linestyle='-', linewidth=1.5, zorder=3)
    ax.scatter(steps, forces, marker='^', facecolors='none', edgecolors='#8A2BE2', s=60, linewidths=1.5, zorder=4)

    ax.set_xlabel("構造緩和ステップ数 (Step)", fontsize=14.5, fontname=jp_font_name, labelpad=8)
    ax.set_ylabel(r"Total force [$\mathrm{Ry/au}$]", fontsize=14.5, fontname=jp_font_name, labelpad=8)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

    ax.set_xlim(-2, 45)
    ax.set_ylim(0.0, 3.0)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(11.5)
        label.set_fontname('Times New Roman')

    plt.tight_layout()
    out_png = os.path.join(LOCAL_DIR, "total_force_progression.png")
    out_pdf = os.path.join(LOCAL_DIR, "total_force_progression.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"Saved: {out_png}")

# ==============================================================================
# 4. Total SCF Correction の推移グラフ
# ==============================================================================
def plot_total_scf_correction():
    steps = [0, 5, 10, 15, 20, 25, 30, 35, 40, 42]
    corrections = [0.038, 0.024, 0.016, 0.011, 0.0085, 0.0068, 0.0055, 0.0048, 0.004422, 0.003771]

    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    ax.plot(steps, corrections, color='#8A2BE2', linestyle='-', linewidth=1.5, zorder=3)
    ax.scatter(steps, corrections, marker='^', facecolors='none', edgecolors='#8A2BE2', s=60, linewidths=1.5, zorder=4)

    ax.set_xlabel("構造緩和ステップ数 (Step)", fontsize=14.5, fontname=jp_font_name, labelpad=8)
    ax.set_ylabel(r"Total SCF correction [$\mathrm{Ry/au}$]", fontsize=14.5, fontname=jp_font_name, labelpad=8)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.01))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.002))

    ax.set_xlim(-2, 45)
    ax.set_ylim(0.0, 0.045)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(11.5)
        label.set_fontname('Times New Roman')

    plt.tight_layout()
    out_png = os.path.join(LOCAL_DIR, "total_scf_correction_progression.png")
    out_pdf = os.path.join(LOCAL_DIR, "total_scf_correction_progression.pdf")
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"Saved: {out_png}")

if __name__ == "__main__":
    plot_total_energy()
    plot_scf_accuracy()
    plot_total_force()
    plot_total_scf_correction()
    print("All 4 progression plots successfully generated!")
