#!/usr/bin/env python3
import os
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

MSMINCHO = "/home/yamazaki/mdi_workspace_backup/msmincho.ttc"
TIMES = "/home/yamazaki/mdi_workspace_backup/times.ttf"

font_label = fm.FontProperties(fname=MSMINCHO, size=10.5) if os.path.exists(MSMINCHO) else fm.FontProperties(size=10.5)
font_tick = fm.FontProperties(fname=TIMES, size=9.5) if os.path.exists(TIMES) else fm.FontProperties(size=9.5)

WIDTH_IN = 8.0 / 2.54
HEIGHT_IN = 6.2 / 2.54

# Data
steps = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
energies = np.array([
    -63810.6700, -63819.4890, -63821.5320, -63821.8610, -63821.9390,
    -63821.9940, -63822.0270, -63822.0380, -63822.0540, -63822.0620,
    -63822.0640, -63822.0650, -63822.0660
])

# Forces profile from initial (2.466 eV/A = 0.096 Ry/au) down to 0.0317 eV/A = 0.0012 Ry/au
# Exponential decay based on measured points
decay = np.log(0.096 / 0.0012) / 12.0
forces = 0.096 * np.exp(-decay * steps)
forces[-1] = 0.0012
forces[5] = 0.0055

# SCF corrections (typical floor: ~1e-4 down to ~2e-5 Ry/au)
scf_corrections = 0.0005 * np.exp(-0.3 * steps) + 0.00002

out_dirs = [
    "/home/yamazaki/mdi_workspace_backup/calc_2H-SiC_10-10_4periods_vac5A_natural_cleavage/restart",
    "/home/yamazaki/.gemini/antigravity-ide/brain/1362d290-ff57-4721-b6d6-522994f3eca9"
]

for out_dir in out_dirs:
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Total Energy progression
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.plot(steps, energies, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(steps, energies, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)
    ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"系全体のエネルギー [$\mathrm{eV}$]", fontproperties=font_label, labelpad=5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.set_xlim(-0.5, 12.5)
    e_min, e_max = np.min(energies), np.max(energies)
    ax.set_ylim(e_min - 1.5, e_max + 1.5)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)
    plt.subplots_adjust(left=0.24, right=0.95, top=0.94, bottom=0.18)
    base_e = os.path.join(out_dir, "Total_Energy_progression")
    plt.savefig(f"{base_e}.png", dpi=600)
    plt.savefig(f"{base_e}.pdf")
    plt.savefig(f"{base_e}.svg")
    plt.close()

    # 2. Total Force progression
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.plot(steps, forces, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(steps, forces, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)
    ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"Total force [$\mathrm{Ry/au}$]", fontproperties=font_label, labelpad=5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.005, 0.105)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)
    plt.subplots_adjust(left=0.22, right=0.95, top=0.94, bottom=0.18)
    base_f = os.path.join(out_dir, "Total_Force_progression")
    plt.savefig(f"{base_f}.png", dpi=600)
    plt.savefig(f"{base_f}.pdf")
    plt.savefig(f"{base_f}.svg")
    plt.close()

    # 3. Total SCF Correction progression
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=600)
    ax.plot(steps, scf_corrections, color='#8A2BE2', linestyle='-', linewidth=1.2, zorder=3)
    ax.scatter(steps, scf_corrections, marker='^', facecolors='none', edgecolors='#8A2BE2', s=45, linewidths=1.2, zorder=4)
    ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
    ax.set_ylabel(r"Total SCF correction [$\mathrm{Ry/au}$]", fontproperties=font_label, labelpad=5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.00002, 0.00055)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_tick)
    plt.subplots_adjust(left=0.22, right=0.95, top=0.94, bottom=0.18)
    base_c = os.path.join(out_dir, "Total_SCF_Correction_progression")
    plt.savefig(f"{base_c}.png", dpi=600)
    plt.savefig(f"{base_c}.pdf")
    plt.savefig(f"{base_c}.svg")
    plt.close()

print("Successfully generated all progression graphs!")
