#!/usr/bin/env python3
"""
generate_unrelaxed_energy_progression_graphs.py
==============================================================================
2H-SiC {10-10} 8周期 (288原子) 真空層 3.0 Å
【構造最適化なし (未緩和初期構造)】300 K NVT-AIMD (100 steps = 100 fs)
エネルギー推移グラフ生成スクリプト (論文・報告書・Word最適化 8.0cm × 6.2cm 600dpi 完全準拠)

1. 全エネルギー推移グラフ (Word 8.0cm × 6.2cm, 600dpi)
2. ポテンシャルエネルギー推移グラフ (Word 8.0cm × 6.2cm, 600dpi)
3. エネルギー成分変化量推移グラフ (ΔE_tot, ΔE_pot, ΔE_kin) (Word 8.0cm × 6.2cm, 600dpi)
4. 総合エネルギー推移グラフ (全成分詳細表示)
==============================================================================
"""

import os
import csv
import numpy as np

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache_sic"
os.makedirs("/tmp/matplotlib_cache_sic", exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

WORKDIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080"
CSV_PATH = os.path.join(WORKDIR, "aimd_unrelaxed_100steps_summary.csv")
MINCHO_PATH = os.path.join(WORKDIR, "msmincho.ttc")
TIMES_PATH = os.path.join(WORKDIR, "times.ttf")

# フォント設定 (AGENTS.md §8 準拠)
prop_mincho_10_5 = fm.FontProperties(fname=MINCHO_PATH, size=10.5)
prop_mincho_9_5 = fm.FontProperties(fname=MINCHO_PATH, size=9.5)
prop_times_9_5 = fm.FontProperties(fname=TIMES_PATH, size=9.5)
prop_times_8_5 = fm.FontProperties(fname=TIMES_PATH, size=8.5)

# データ読み込み
rows = []
with open(CSV_PATH, "r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({k: float(v) for k, v in r.items()})

t = np.array([r["time_fs"] for r in rows])
etot = np.array([r["etotal_eV"] for r in rows])
pe = np.array([r["pe_eV"] for r in rows])
ke = np.array([r["ke_eV"] for r in rows])
temp = np.array([r["temp_K"] for r in rows])

# 初期値からの変化量
delta_etot = etot - etot[0]
delta_pe = pe - pe[0]
delta_ke = ke - ke[0]

# 共通寸法: Word 8.0 cm × 6.2 cm (約 3.15 × 2.44 インチ)
W_INCH = 8.0 / 2.54
H_INCH = 6.2 / 2.54

# ==============================================================================
# グラフ 1: 全エネルギー推移 (Word 8.0 cm × 6.2 cm, 600 dpi)
# ==============================================================================
fig, ax = plt.subplots(figsize=(W_INCH, H_INCH), dpi=600)
ax.plot(
    t, etot,
    color="#8A2BE2",
    lw=1.2,
    marker="^",
    markersize=4.5,
    markerfacecolor="none",
    markeredgecolor="#8A2BE2",
    markeredgewidth=1.0,
    markevery=5,  # 5ステップごとにマーカー配置
)
ax.set_xlabel("時間 [$\\mathrm{fs}$]", fontproperties=prop_mincho_10_5)
ax.set_ylabel("全エネルギー [$\\mathrm{eV}$]", fontproperties=prop_mincho_10_5)
ax.set_xlim(0, 100)
ax.set_ylim(-127663.2, -127662.2)

ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.2))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(prop_times_9_5)

ax.tick_params(direction="in", top=True, right=True, which="both", width=0.8)
ax.tick_params(which="major", length=4.5)
ax.tick_params(which="minor", length=2.5)
for spine in ax.spines.values():
    spine.set_linewidth(0.8)
ax.grid(True, linestyle=":", linewidth=0.5, color="#CCCCCC", alpha=0.7)

plt.tight_layout(pad=0.4)
for ext in ["png", "pdf", "svg"]:
    out_path = os.path.join(WORKDIR, f"全エネルギー推移_未緩和AIMD_word_8cm.{ext}")
    fig.savefig(out_path, dpi=600)
plt.close(fig)

# ==============================================================================
# グラフ 2: ポテンシャルエネルギー推移 (Word 8.0 cm × 6.2 cm, 600 dpi)
# ==============================================================================
fig, ax = plt.subplots(figsize=(W_INCH, H_INCH), dpi=600)
ax.plot(
    t, pe,
    color="#1E90FF",
    lw=1.2,
    marker="^",
    markersize=4.5,
    markerfacecolor="none",
    markeredgecolor="#1E90FF",
    markeredgewidth=1.0,
    markevery=5,
)
ax.set_xlabel("時間 [$\\mathrm{fs}$]", fontproperties=prop_mincho_10_5)
ax.set_ylabel("ポテンシャルエネルギー [$\\mathrm{eV}$]", fontproperties=prop_mincho_10_5)
ax.set_xlim(0, 100)
ax.set_ylim(-127678.5, -127670.5)

ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(2.0))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(prop_times_9_5)

ax.tick_params(direction="in", top=True, right=True, which="both", width=0.8)
ax.tick_params(which="major", length=4.5)
ax.tick_params(which="minor", length=2.5)
for spine in ax.spines.values():
    spine.set_linewidth(0.8)
ax.grid(True, linestyle=":", linewidth=0.5, color="#CCCCCC", alpha=0.7)

plt.tight_layout(pad=0.4)
for ext in ["png", "pdf", "svg"]:
    out_path = os.path.join(WORKDIR, f"ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.{ext}")
    fig.savefig(out_path, dpi=600)
plt.close(fig)

# ==============================================================================
# グラフ 3: エネルギー成分変化量推移 (ΔE_tot, ΔE_pot, ΔE_kin) (Word 8.0 cm × 6.2 cm, 600 dpi)
# ==============================================================================
fig, ax = plt.subplots(figsize=(W_INCH, H_INCH), dpi=600)
ax.plot(
    t, delta_pe,
    color="#1E90FF",
    lw=1.2,
    linestyle="-",
    marker="o",
    markersize=3.5,
    markerfacecolor="none",
    markeredgecolor="#1E90FF",
    markeredgewidth=0.9,
    markevery=6,
    label="$\\Delta E_{\\mathrm{pot}}$ (ポテンシャル)",
)
ax.plot(
    t, delta_ke,
    color="#FF4500",
    lw=1.2,
    linestyle="--",
    marker="s",
    markersize=3.5,
    markerfacecolor="none",
    markeredgecolor="#FF4500",
    markeredgewidth=0.9,
    markevery=6,
    label="$\\Delta E_{\\mathrm{kin}}$ (運動)",
)
ax.plot(
    t, delta_etot,
    color="#8A2BE2",
    lw=1.4,
    linestyle="-",
    marker="^",
    markersize=4.0,
    markerfacecolor="none",
    markeredgecolor="#8A2BE2",
    markeredgewidth=1.0,
    markevery=6,
    label="$\\Delta E_{\\mathrm{total}}$ (全エネルギー)",
)
ax.axhline(0, color="#666666", linestyle=":", linewidth=0.8)

ax.set_xlabel("時間 [$\\mathrm{fs}$]", fontproperties=prop_mincho_10_5)
ax.set_ylabel("エネルギー変化量 [$\\mathrm{eV}$]", fontproperties=prop_mincho_10_5)
ax.set_xlim(0, 100)
ax.set_ylim(-4.5, 4.5)

ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(2.0))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(prop_times_9_5)

ax.tick_params(direction="in", top=True, right=True, which="both", width=0.8)
ax.tick_params(which="major", length=4.5)
ax.tick_params(which="minor", length=2.5)
for spine in ax.spines.values():
    spine.set_linewidth(0.8)
ax.grid(True, linestyle=":", linewidth=0.5, color="#CCCCCC", alpha=0.7)

ax.legend(prop=prop_mincho_9_5, loc="center right", frameon=True, framealpha=0.9, edgecolor="#CCCCCC", borderpad=0.3)

plt.tight_layout(pad=0.4)
for ext in ["png", "pdf", "svg"]:
    out_path = os.path.join(WORKDIR, f"エネルギー変化量推移_未緩和AIMD_word_8cm.{ext}")
    fig.savefig(out_path, dpi=600)
plt.close(fig)

# ==============================================================================
# グラフ 4: 総合エネルギー推移 (プレゼンテーション・長方形仕様 5.6 × 4.4 インチ, 300 dpi)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.6, 4.6), dpi=300, sharex=True)

# 上段: 全エネルギー (保存性の確認)
ax1.plot(t, etot, color="#8A2BE2", lw=1.5, marker="^", markersize=4, markerfacecolor="none", markeredgecolor="#8A2BE2", markevery=5, label="全エネルギー $E_{\\mathrm{total}}$ (保存量)")
ax1.set_ylabel("全エネルギー [$\\mathrm{eV}$]", fontproperties=prop_mincho_10_5)
ax1.set_ylim(-127663.2, -127662.2)
ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
for label in ax1.get_xticklabels() + ax1.get_yticklabels():
    label.set_fontproperties(prop_times_9_5)
ax1.tick_params(direction="in", top=True, right=True, which="both")
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(prop=prop_mincho_9_5, loc="upper right", frameon=True)

# 下段: ポテンシャルエネルギーと運動エネルギーの相互変換
ax2.plot(t, pe, color="#1E90FF", lw=1.5, label="ポテンシャルエネルギー $E_{\\mathrm{pot}}$")
ax2_twin = ax2.twinx()
ax2_twin.plot(t, ke, color="#FF4500", lw=1.5, linestyle="--", label="運動エネルギー $E_{\\mathrm{kin}}$")

ax2.set_xlabel("時間 [$\\mathrm{fs}$]", fontproperties=prop_mincho_10_5)
ax2.set_ylabel("ポテンシャル $E_{\\mathrm{pot}}$ [$\\mathrm{eV}$]", fontproperties=prop_mincho_10_5, color="#1E90FF")
ax2_twin.set_ylabel("運動エネルギー $E_{\\mathrm{kin}}$ [$\\mathrm{eV}$]", fontproperties=prop_mincho_10_5, color="#FF4500")

ax2.set_xlim(0, 100)
ax2.set_ylim(-127678.5, -127670.5)
ax2_twin.set_ylim(8.0, 16.0)

for label in ax2.get_xticklabels() + ax2.get_yticklabels():
    label.set_fontproperties(prop_times_9_5)
for label in ax2_twin.get_yticklabels():
    label.set_fontproperties(prop_times_9_5)

ax2.tick_params(direction="in", top=True, right=False)
ax2_twin.tick_params(direction="in", top=True, right=True)
ax2.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
for ext in ["png", "pdf", "svg"]:
    out_path = os.path.join(WORKDIR, f"エネルギー総合推移_未緩和AIMD_プレゼン仕様.{ext}")
    fig.savefig(out_path, dpi=300)
plt.close(fig)

print("All energy progression graphs generated successfully.")

