#!/usr/bin/env python3
"""
generate_6periods_progression_graphs.py
6周期 (12層, 216原子) スラブ構造緩和の推移グラフ生成スクリプト
GRAPH_STYLE_SPEC.md & ワークスペース恒久ルール8 準拠:
- 寸法: 横 8.0 cm x 縦 6.2 cm (Word 二段組最適化)
- 4辺枠線, 内向き目盛り
- フォント: MS明朝 (軸ラベル 10.5 pt), Times New Roman (目盛り 9.5 pt), 数式 STIX
- 中抜き紫三角マーカー (#8A2BE2) + 折れ線
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

# スタイル設定
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

WIN_FONTS = "/mnt/c/Windows/Fonts"
MSMINCHO = os.path.join(WIN_FONTS, "msmincho.ttc")
TIMES = os.path.join(WIN_FONTS, "times.ttf")

font_label = fm.FontProperties(fname=MSMINCHO, size=10.5) if os.path.exists(MSMINCHO) else fm.FontProperties(size=10.5)
font_tick = fm.FontProperties(fname=TIMES, size=9.5) if os.path.exists(TIMES) else fm.FontProperties(size=9.5)

WORK_DIR = "/home/yamazaki/mdi_workspace_backup/calc_2H-SiC_10-10_6periods_vac5A"
WIDTH_IN = 8.0 / 2.54
HEIGHT_IN = 6.2 / 2.54

def parse_data():
    lmp_log = os.path.join(WORK_DIR, "lmp.log")
    steps = []
    energies = []
    
    with open(lmp_log, "r", errors="ignore") as f:
        in_thermo = False
        for line in f:
            if "Step" in line and "TotEng" in line:
                in_thermo = True
                continue
            if in_thermo:
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0].isdigit():
                    s = int(parts[0])
                    e = float(parts[4])
                    steps.append(s)
                    energies.append(e)
                elif "Loop time" in line:
                    in_thermo = False
                    
    # CSV 保存
    csv_path = os.path.join(WORK_DIR, "lammps_steps_energy.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["LAMMPS_Step", "TotEng_eV"])
        for s, e in zip(steps, energies):
            writer.writerow([s, e])
    print(f"Saved {len(steps)} steps to {csv_path}")
    return steps, energies

def plot_total_energy(steps, energies):
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN))
    
    # プロット
    ax.plot(steps, energies, color='#8A2BE2', lw=1.2, zorder=2)
    ax.scatter(steps, energies, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=3)
    
    # 軸ラベル
    ax.set_xlabel(r"構造緩和ステップ数 [$\mathrm{Step}$]", fontproperties=font_label, labelpad=5.0)
    ax.set_ylabel(r"系全体のエネルギー [$\mathrm{eV}$]", fontproperties=font_label, labelpad=5.0)
    
    # 目盛り設定
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.set_xlim(-1, max(steps) + 2)
    
    # Y軸
    y_min, y_max = min(energies), max(energies)
    margin = (y_max - y_min) * 0.05
    ax.set_ylim(y_min - margin, y_max + margin)
    
    for label in ax.get_xticklabels():
        label.set_fontproperties(font_tick)
    for label in ax.get_yticklabels():
        label.set_fontproperties(font_tick)
        
    plt.tight_layout(pad=0.4)
    
    for ext in ["png", "pdf", "svg"]:
        out_f = os.path.join(WORK_DIR, f"Total_Energy_progression.{ext}")
        plt.savefig(out_f, dpi=600 if ext == 'png' else None)
        print(f"Generated: {out_f}")
    plt.close()

def main():
    steps, energies = parse_data()
    plot_total_energy(steps, energies)

if __name__ == "__main__":
    main()
