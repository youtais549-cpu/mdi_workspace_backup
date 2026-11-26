#!/usr/bin/env python3
"""
generate_8periods_comparison_graph.py
2H-SiC {10-10} 表面破壊エネルギーの「周期数」依存性グラフ (2, 4, 6, 8周期, 真空層 5.0 Å 固定)
既存ファイル (周期数と表面破壊エネルギーの関係.*) を上書きせず、
新規ファイル (周期数と表面破壊エネルギーの関係_8周期追加.*) として保存する。
"""
import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['svg.fonttype'] = 'path'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)

CONV = 16.021766
AREA_2A = 279.497664

# 各条件の生ログから算出した確定値 (真空層 5.0 Å 統一)
data = [
    (2, -31892.6430, -31935.3572, "2 periods (72 atoms, vac 5A)"),
    (4, -63822.0658, -63863.3059, "4 periods (144 atoms, vac 5A)"),
    (6, -95753.5368, -95794.2985, "6 periods (216 atoms, vac 5A)"),
    (8, -127685.0579, -127726.1628, "8 periods (288 atoms, vac 5A)"),
]

rows = []
for n, es, eb, note in data:
    de = es - eb
    g = (de / AREA_2A) * CONV
    rows.append((n, es, eb, de, g, note))

csv_out = os.path.join(SCRIPT_DIR, "surface_energy_vs_periods_2_4_6_8_data.csv")
with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Periods", "Vacuum_A", "E_slab_eV", "E_bulk_eV", "Delta_E_eV", "Area_2A_A2", "Gamma_J_m2", "Note"])
    for n, es, eb, de, g, note in rows:
        w.writerow([n, 5.0, es, eb, round(de, 4), round(AREA_2A, 4), round(g, 4), note])

mincho = os.path.join(SCRIPT_DIR, "msmincho.ttc")
times = os.path.join(SCRIPT_DIR, "times.ttf")

x_pts = [r[0] for r in rows]
y_pts = [r[4] for r in rows]
LIT_VAL = 3.03


def plot_graph(width_in, height_in, dpi, label_size, tick_size, lit_size, msize, lw_box, suffix):
    plt.rcParams['axes.linewidth'] = lw_box
    f_label = fm.FontProperties(fname=mincho, size=label_size)
    f_tick = fm.FontProperties(fname=times, size=tick_size)
    f_lit = fm.FontProperties(fname=mincho, size=lit_size)

    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
    ax.scatter(x_pts, y_pts, marker='^', facecolors='none', edgecolors='#8A2BE2', s=msize, linewidths=1.6, zorder=5)
    ax.axhline(LIT_VAL, color='#222222', linestyle='--', linewidth=1.2, zorder=2)
    ax.text(2.3, LIT_VAL + 0.025, "文献値 (3.03 J/m²)", fontproperties=f_lit, color='#222222')

    ax.set_xlim(1.0, 9.0)
    ax.set_ylim(2.2, 3.2)
    ax.set_xlabel("周期数 [Periods]", fontproperties=f_label, labelpad=6)
    ax.set_ylabel(r"表面破壊エネルギー [$\mathrm{J/m^2}$]", fontproperties=f_label, labelpad=6)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(1.0))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(f_tick)

    plt.subplots_adjust(left=0.20, right=0.95, top=0.94, bottom=0.18)

    for out_dir in [SCRIPT_DIR, WORKSPACE_DIR]:
        base = os.path.join(out_dir, f"周期数と表面破壊エネルギーの関係_8周期追加{suffix}")
        plt.savefig(f"{base}.png", dpi=dpi)
        plt.savefig(f"{base}.pdf")
        plt.savefig(f"{base}.svg")
    plt.close()


if __name__ == "__main__":
    # 1. 標準サイズ (5.6 x 4.4 inch, 300 dpi)
    plot_graph(5.6, 4.4, 300, 14.5, 11.5, 12.0, 75, 1.3, "")
    # 2. Word 8.0cm x 6.2cm サイズ (600 dpi)
    plot_graph(8.0 / 2.54, 6.2 / 2.54, 600, 10.5, 9.5, 9.0, 55, 1.2, "_word_8cm")
    print("Generated 2-4-6-8 periods comparison graphs successfully!")
