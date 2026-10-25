#!/usr/bin/env python3
"""
generate_surface_energy_vs_periods_graph.py
2H-SiC {10-10} 表面破壊エネルギーの「周期数」依存性グラフ (真空層 5.0 Å 固定)
【自然へき開面・完全緩和更新版】

体裁仕様:
- 横 8.0 cm x 縦 6.2 cm, 4辺枠線, 内向き目盛り
- 軸ラベル MS明朝 10.5 pt / 目盛り Times New Roman 9.5 pt / 単位 STIX
- 中抜き紫三角マーカー (線なし), 文献値 3.03 J/m^2 の水平破線
- 縦軸: 2.2 ~ 3.2 J/m^2 (0.1 刻み)
- 横軸: 0 ~ 6 周期 (1.0 刻み)
"""
import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, TextArea

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

ROOT = "/home/yamazaki/mdi_workspace_backup"
CONV = 16.021766          # eV/Å^2 -> J/m^2
AREA_2A = 279.4977        # Å^2 (3x3 面内セル, 上下 2 面)

# 2 周期 (72 原子, 真空 5 Å, CG 収束済み)
E_SLAB_2P = -31892.6430
E_BULK_72 = -31935.3572

# 4 周期 (144 原子, 自然へき開面, 完全緩和済み)
E_SLAB_4P = -63822.0658
E_BULK_144 = -63863.3059

data = [
    (2, E_SLAB_2P, E_BULK_72, "converged (72 atoms, vac 5A)"),
    (4, E_SLAB_4P, E_BULK_144, "converged (144 atoms, natural cleavage vac 5A)"),
]

rows = []
for n, es, eb, note in data:
    de = es - eb
    g = de / AREA_2A * CONV
    rows.append((n, es, eb, de, g, note))
    print(f"{n} periods: E_slab={es:.4f}  E_bulk={eb:.4f}  dE={de:.4f} eV  gamma={g:.4f} J/m2  [{note}]")

csv_path = os.path.join(ROOT, "surface_energy_vs_periods_plot_data.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Periods", "Vacuum_A", "E_slab_eV", "E_bulk_eV", "Delta_E_eV", "Area_2A_A2", "Gamma_J_m2", "Note"])
    for n, es, eb, de, g, note in rows:
        w.writerow([n, 5.0, es, eb, round(de, 4), AREA_2A, round(g, 4), note])

# フォント
mincho = "/home/yamazaki/mdi_workspace_backup/msmincho.ttc"
times = "/home/yamazaki/mdi_workspace_backup/times.ttf"

fp = lambda path, **kw: fm.FontProperties(fname=path, **kw) if os.path.exists(path) else fm.FontProperties(**kw)
f_label = fp(mincho, size=10.5)
f_lit_jp = fp(mincho, weight="bold", size=9.5)
f_tick = fp(times, size=9.5)
f_lit_en = fp(times, weight="bold", size=9.5)

WIDTH_IN = 8.0 / 2.54
HEIGHT_IN = 6.2 / 2.54

fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)

# プロット点
x_pts = [r[0] for r in rows]
y_pts = [r[4] for r in rows]
ax.scatter(x_pts, y_pts, marker='^', facecolors='none', edgecolors='#8A2BE2', s=55, linewidths=1.3, zorder=5)

# 文献値線 (3.03 J/m^2)
LIT_VAL = 3.03
ax.axhline(LIT_VAL, color='#222222', linestyle='--', linewidth=1.1, zorder=2)

# 文献値ラベル
t_jp = TextArea("文献値 ", textprops=dict(fontproperties=f_lit_jp, color='#222222'))
t_en = TextArea(f"({LIT_VAL:.2f} J/m²)", textprops=dict(fontproperties=f_lit_en, color='#222222'))
box = HPacker(children=[t_jp, t_en], align="baseline", pad=0, sep=0)
anchored = AnchoredOffsetbox(
    loc="lower right",
    child=box,
    pad=0.0,
    borderpad=0.3,
    frameon=False,
    bbox_to_anchor=(0.95, (LIT_VAL - 2.2) / (3.2 - 2.2) + 0.02),
    bbox_transform=ax.transAxes,
)
ax.add_artist(anchored)

# Rauls et al. 1999 の緩和後文献値基準線 (2.27 J/m^2) も追加
LIT_RELAXED = 2.27
ax.axhline(LIT_RELAXED, color='#008080', linestyle=':', linewidth=1.0, zorder=2)
t_r_jp = TextArea("Rauls緩和値 ", textprops=dict(fontproperties=fp(mincho, size=8.5), color='#008080'))
t_r_en = TextArea("(2.27 J/m²)", textprops=dict(fontproperties=fp(times, size=8.5), color='#008080'))
box_r = HPacker(children=[t_r_jp, t_r_en], align="baseline", pad=0, sep=0)
anchored_r = AnchoredOffsetbox(
    loc="lower right",
    child=box_r,
    pad=0.0,
    borderpad=0.3,
    frameon=False,
    bbox_to_anchor=(0.95, (LIT_RELAXED - 2.2) / (3.2 - 2.2) + 0.02),
    bbox_transform=ax.transAxes,
)
ax.add_artist(anchored_r)

# 軸範囲と目盛り
ax.set_xlim(0.0, 6.0)
ax.set_ylim(2.2, 3.2)

ax.set_xlabel("周期数 [Period]", fontproperties=f_label, labelpad=5)
ax.set_ylabel(r"表面破壊エネルギー [$\mathrm{J/m^2}$]", fontproperties=f_label, labelpad=5)

ax.xaxis.set_major_locator(ticker.MultipleLocator(1.0))
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.05))

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(f_tick)

plt.subplots_adjust(left=0.20, right=0.95, top=0.94, bottom=0.18)

out_destinations = [
    ROOT,
    "/home/yamazaki/.gemini/antigravity-ide/brain/1362d290-ff57-4721-b6d6-522994f3eca9",
    "/home/yamazaki/mdi_workspace_backup/calc_2H-SiC_10-10_4periods_vac5A_natural_cleavage/restart"
]

for d in out_destinations:
    os.makedirs(d, exist_ok=True)
    base = os.path.join(d, "surface_energy_vs_periods_vac5A")
    plt.savefig(f"{base}.png", dpi=600)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")

print("Successfully saved updated surface_energy_vs_periods_vac5A graphs!")
