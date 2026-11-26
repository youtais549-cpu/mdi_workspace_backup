#!/usr/bin/env python3
"""
generate_default_surface_energy_graphs.py
2H-SiC {10-10} 表面破壊エネルギーの真空層厚さ依存性グラフ生成スクリプト
(承認済みデフォルト仕様 GRAPH_STYLE_SPEC.md 厳格準拠)

【仕様】
1. デフォルト標準仕様 (GRAPH_STYLE_SPEC.md):
   - 形状: 5.6 x 4.4 インチ (300 dpi)
   - 縦軸: 0.0 〜 5.0 J/m² (1.0 刻み, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, Times New Roman 11.5 pt)
   - 横軸: 0.0 〜 16.0 Å (2.0 刻み, 2.0, 4.0, 6.0, ... 16.0, 原点 0.0 は縦軸と共用して非表示)
   - ラベル: 縦軸 `表面破壊エネルギー  $\mathrm{[J/m^2]}$`, 横軸 `真空層の厚さ  $\mathrm{[\AA]}$` (14.5 pt)
   - マーカー: 中抜き紫三角 (marker='^', facecolors='none', edgecolors='#8A2BE2', s=70, linewidths=1.6)
   - 基準線: y=3.03 J/m² 水平破線 (linestyle='--', color='#222222', linewidth=1.2)
   - 注記: HPacker による太字「文献値」+ Times New Roman Bold「(3.03 J/m²)」

2. Word 文書最適化仕様 (generate_final_graph.py 準拠):
   - 形状: 8.0 cm x 6.2 cm (600 dpi, 余白固定)
   - 軸ラベル: 10.5 pt, 目盛り数字: 9.5 pt

3. プラトー拡大仕様 (AGENTS.md §7 準拠):
   - 縦軸: 2.2 〜 3.2 J/m² (0.1 刻み) で 1.5 Å 〜 10.0 Å の収束領域を詳細可視化
"""

import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, TextArea
import matplotlib.ticker as ticker

# 数式フォントに STIX (Times New Roman 互換) を適用
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["svg.fonttype"] = "path"

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(WORKSPACE_DIR, "vacuum_sweep_2periods_0.5_to_10A_results.csv")

# フォントパス解決
mincho_path = os.path.join(WORKSPACE_DIR, "msmincho.ttc")
times_path = os.path.join(WORKSPACE_DIR, "times.ttf")
timesbd_path = os.path.join(WORKSPACE_DIR, "timesbd.ttf")

if not os.path.exists(mincho_path):
    mincho_path = "/mnt/c/Windows/Fonts/msmincho.ttc"
if not os.path.exists(times_path):
    times_path = "/mnt/c/Windows/Fonts/times.ttf"
if not os.path.exists(timesbd_path):
    timesbd_path = "/mnt/c/Windows/Fonts/timesbd.ttf"

def load_sweep_data():
    x_vals = []
    y_vals = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vac = float(row["Vacuum_A"])
            gamma = float(row["Gamma_J_m2"])
            x_vals.append(vac)
            y_vals.append(gamma)
    return x_vals, y_vals

def generate_default_standard_graph(x_vals, y_vals):
    """GRAPH_STYLE_SPEC.md 承認済みデフォルト標準仕様 (5.6 x 4.4 インチ, 300 dpi)"""
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    # 1. データ点プロット (線なし・中抜き紫三角)
    ax.scatter(
        x_vals,
        y_vals,
        color="#8A2BE2",
        marker="^",
        s=70,
        edgecolors="#8A2BE2",
        linewidths=1.6,
        facecolors="none",
        zorder=5
    )

    # 2. 文献値の水平破線 (3.03 J/m²)
    lit_val = 3.03
    ax.axhline(
        y=lit_val,
        color="#222222",
        linestyle="--",
        linewidth=1.2,
        zorder=3
    )

    # 3. 文献値テキスト (太字日本語 + Times New Roman Bold)
    font_lit_jp = fm.FontProperties(fname=mincho_path, weight="bold", size=12)
    font_lit_en = fm.FontProperties(fname=timesbd_path, weight="bold", size=12.5)

    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_lit_jp, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_lit_en, color="#111111"))
    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=3)

    y_norm = (lit_val / 5.0) + 0.024
    anchored_box = AnchoredOffsetbox(
        loc="lower right",
        child=packer,
        pad=0.0,
        frameon=False,
        bbox_to_anchor=(0.96, y_norm),
        bbox_transform=ax.transAxes
    )
    ax.add_artist(anchored_box)

    # 4. 軸範囲の設定
    ax.set_xlim(0.0, 16.0)
    ax.set_ylim(0.0, 5.0)

    # 5. 目盛りの設定 (Times New Roman 11.5 pt, 原点 0.0 は縦軸と共用)
    font_tick = fm.FontProperties(fname=times_path, size=11.5)

    x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    ax.set_xticks(x_ticks)
    x_labels = ["" if x == 0.0 else f"{x:.1f}" for x in x_ticks]
    ax.set_xticklabels(x_labels, fontproperties=font_tick)

    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_tick)

    # 6. 軸ラベルの設定 (14.5 pt)
    font_label = fm.FontProperties(fname=mincho_path, size=14.5)
    ax.set_xlabel(r"真空層の厚さ  $\mathrm{[\AA]}$", fontproperties=font_label, labelpad=10)
    ax.set_ylabel(r"表面破壊エネルギー  $\mathrm{[J/m^2]}$", fontproperties=font_label, labelpad=10)

    # 7. 枠線および目盛り線のスタイル (内向き, 4辺全囲み)
    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.1)

    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=5.5,
        width=1.0,
        top=True,
        right=True,
        bottom=True,
        left=True,
        pad=6.0
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.subplots_adjust(left=0.17, right=0.95, bottom=0.17, top=0.95)

    base = os.path.join(WORKSPACE_DIR, "真空層の厚さと表面破壊エネルギーの関係_デフォルト仕様")
    plt.savefig(f"{base}.png", dpi=300)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"✅ デフォルト標準仕様グラフ生成完了: {base}.png/.pdf/.svg")

def generate_word_optimized_graph(x_vals, y_vals):
    """Word 文書最適化仕様 (横 8.0 cm x 縦 6.2 cm, 600 dpi)"""
    w_in = 8.0 / 2.54
    h_in = 6.2 / 2.54

    fig, ax = plt.subplots(figsize=(w_in, h_in), dpi=600)
    fig.subplots_adjust(left=0.21, right=0.94, bottom=0.20, top=0.96)

    # データ点
    ax.scatter(
        x_vals,
        y_vals,
        color="#8A2BE2",
        marker="^",
        s=45,
        linewidths=1.3,
        facecolors="none",
        zorder=4
    )

    # 文献値 (3.03 J/m²)
    lit_val = 3.03
    ax.axhline(y=lit_val, color="#222222", linestyle="--", linewidth=1.0, zorder=3)

    font_mincho_lit = fm.FontProperties(fname=mincho_path, weight="bold", size=9.5)
    font_times_lit = fm.FontProperties(fname=timesbd_path, weight="bold", size=9.5)
    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_mincho_lit, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_times_lit, color="#111111"))
    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=2)

    y_norm = (lit_val / 5.0) + 0.026
    anchored_box = AnchoredOffsetbox(
        loc="lower right",
        child=packer,
        pad=0.0,
        frameon=False,
        bbox_to_anchor=(0.95, y_norm),
        bbox_transform=ax.transAxes
    )
    ax.add_artist(anchored_box)

    # 軸範囲
    ax.set_xlim(0.0, 16.0)
    ax.set_ylim(0.0, 5.0)

    font_times_tick = fm.FontProperties(fname=times_path, size=9.5)
    font_mincho_label = fm.FontProperties(fname=mincho_path, size=10.5)

    x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(["" if x == 0.0 else f"{x:.1f}" for x in x_ticks], fontproperties=font_times_tick)

    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_times_tick)

    ax.set_xlabel(r"真空層の厚さ $\mathrm{[\AA]}$", fontproperties=font_mincho_label, labelpad=3)
    ax.set_ylabel(r"表面破壊エネルギー $\mathrm{[J/m^2]}$", fontproperties=font_mincho_label, labelpad=4)

    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(0.8)

    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=3.5,
        width=0.8,
        top=True,
        right=True,
        bottom=True,
        left=True,
        pad=3.5
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    base = os.path.join(WORKSPACE_DIR, "真空層の厚さと表面破壊エネルギーの関係_Word最適化仕様")
    plt.savefig(f"{base}.png", dpi=600)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"✅ Word最適化仕様グラフ生成完了: {base}.png/.pdf/.svg")

def generate_plateau_zoom_graph(x_vals, y_vals):
    """プラトー拡大仕様 (1.5 Å 〜 10.0 Å の収束域を 2.2 〜 3.2 J/m² で拡大表示)"""
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    # 0.5Å, 1.0Å は再結合領域 (1.21, 0.21) のため、結合切断後の 1.5Å〜10.0Å をプロット
    x_zoom = [x for x, y in zip(x_vals, y_vals) if y >= 2.0]
    y_zoom = [y for x, y in zip(x_vals, y_vals) if y >= 2.0]

    ax.scatter(
        x_zoom,
        y_zoom,
        color="#8A2BE2",
        marker="^",
        s=70,
        edgecolors="#8A2BE2",
        linewidths=1.6,
        facecolors="none",
        zorder=5
    )

    # 文献値 (3.03 J/m²)
    lit_val = 3.03
    ax.axhline(y=lit_val, color="#222222", linestyle="--", linewidth=1.2, zorder=3)

    font_lit_jp = fm.FontProperties(fname=mincho_path, weight="bold", size=12)
    font_lit_en = fm.FontProperties(fname=timesbd_path, weight="bold", size=12.5)
    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_lit_jp, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_lit_en, color="#111111"))
    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=3)

    # y=3.03 の破線直上 (ylim 2.2〜3.2 に対する正規化)
    y_norm = (lit_val - 2.2) / (3.2 - 2.2) + 0.024
    anchored_box = AnchoredOffsetbox(
        loc="lower right",
        child=packer,
        pad=0.0,
        frameon=False,
        bbox_to_anchor=(0.96, y_norm),
        bbox_transform=ax.transAxes
    )
    ax.add_artist(anchored_box)

    ax.set_xlim(0.0, 16.0)
    ax.set_ylim(2.2, 3.2)

    font_tick = fm.FontProperties(fname=times_path, size=11.5)
    x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"{x:.1f}" for x in x_ticks], fontproperties=font_tick)

    y_ticks = [2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_tick)

    font_label = fm.FontProperties(fname=mincho_path, size=14.5)
    ax.set_xlabel(r"真空層の厚さ  $\mathrm{[\AA]}$", fontproperties=font_label, labelpad=10)
    ax.set_ylabel(r"表面破壊エネルギー  $\mathrm{[J/m^2]}$", fontproperties=font_label, labelpad=10)

    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.1)

    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=5.5,
        width=1.0,
        top=True,
        right=True,
        bottom=True,
        left=True,
        pad=6.0
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.subplots_adjust(left=0.17, right=0.95, bottom=0.17, top=0.95)

    base = os.path.join(WORKSPACE_DIR, "真空層の厚さと表面破壊エネルギーの関係_プラトー拡大仕様")
    plt.savefig(f"{base}.png", dpi=300)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"✅ プラトー拡大仕様グラフ生成完了: {base}.png/.pdf/.svg")

def generate_full_range_graph(x_vals, y_vals):
    """全域表示仕様 (0.0 Å の 7.98 J/m² を含む 0.0 〜 9.0 J/m² フルレンジ表示)"""
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    ax.scatter(
        x_vals,
        y_vals,
        color="#8A2BE2",
        marker="^",
        s=70,
        edgecolors="#8A2BE2",
        linewidths=1.6,
        facecolors="none",
        zorder=5
    )

    lit_val = 3.03
    ax.axhline(
        y=lit_val,
        color="#222222",
        linestyle="--",
        linewidth=1.2,
        zorder=3
    )

    font_lit_jp = fm.FontProperties(fname=mincho_path, weight="bold", size=12)
    font_lit_en = fm.FontProperties(fname=timesbd_path, weight="bold", size=12.5)

    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_lit_jp, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_lit_en, color="#111111"))
    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=3)

    y_norm = (lit_val / 9.0) + 0.024
    anchored_box = AnchoredOffsetbox(
        loc="lower right",
        child=packer,
        pad=0.0,
        frameon=False,
        bbox_to_anchor=(0.96, y_norm),
        bbox_transform=ax.transAxes
    )
    ax.add_artist(anchored_box)

    ax.set_xlim(0.0, 16.0)
    ax.set_ylim(0.0, 9.0)

    font_tick = fm.FontProperties(fname=times_path, size=11.5)
    x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(["" if x == 0.0 else f"{x:.1f}" for x in x_ticks], fontproperties=font_tick)

    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_tick)

    font_label = fm.FontProperties(fname=mincho_path, size=14.5)
    ax.set_xlabel(r"真空層の厚さ  $\mathrm{[\AA]}$", fontproperties=font_label, labelpad=10)
    ax.set_ylabel(r"表面破壊エネルギー  $\mathrm{[J/m^2]}$", fontproperties=font_label, labelpad=10)

    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.1)

    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=5.5,
        width=1.0,
        top=True,
        right=True,
        bottom=True,
        left=True,
        pad=6.0
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.subplots_adjust(left=0.17, right=0.95, bottom=0.17, top=0.95)

    base = os.path.join(WORKSPACE_DIR, "真空層の厚さと表面破壊エネルギーの関係_全域表示仕様")
    plt.savefig(f"{base}.png", dpi=300)
    plt.savefig(f"{base}.pdf")
    plt.savefig(f"{base}.svg")
    plt.close()
    print(f"✅ 全域表示仕様グラフ生成完了: {base}.png/.pdf/.svg")


if __name__ == "__main__":
    x_vals, y_vals = load_sweep_data()
    print(f"Loaded {len(x_vals)} data points: x in [{min(x_vals)}, {max(x_vals)}], y in [{min(y_vals)}, {max(y_vals)}]")
    generate_default_standard_graph(x_vals, y_vals)
    generate_full_range_graph(x_vals, y_vals)
    generate_word_optimized_graph(x_vals, y_vals)
    generate_plateau_zoom_graph(x_vals, y_vals)

