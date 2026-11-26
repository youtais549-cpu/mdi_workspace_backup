#!/usr/bin/env python3
"""
plot_surface_energy_preview.py
表面破壊エネルギーの真空層厚さ依存性グラフ (体裁確認用プレビュー v2)

【ユーザーからの修正指示の反映】:
  1. 縦軸と横軸の表題の文字サイズを大きく (14.5 pt)
  2. 表題の単位・英数字を Times New Roman (STIX Times互換) に設定
  3. 文献値 (3.03 J/m²) を太字に変更:
     - 「文献値」: 太字日本語フォント
     - 「(3.03 J/m²)」: 本物の Times New Roman Bold (太字)
  4. 目盛りの数字 (0.0, 1.0, 2.0... / 2.0, 4.0, 6.0...) もすべて Times New Roman
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, TextArea
import japanize_matplotlib

# STIX フォントセット (Times New Roman 互換) を mathtext に適用
plt.rcParams['mathtext.fontset'] = 'stix'

# Windows フォントの定義
FP_TIMES = fm.FontProperties(fname="/mnt/c/Windows/Fonts/times.ttf")
FP_TIMES_BOLD = fm.FontProperties(fname="/mnt/c/Windows/Fonts/timesbd.ttf")
FP_GOTHIC = fm.FontProperties(fname="/mnt/c/Windows/Fonts/msgothic.ttc")
FP_GOTHIC_BOLD = fm.FontProperties(fname="/mnt/c/Windows/Fonts/msgothic.ttc", weight="bold")
FP_MINCHO = fm.FontProperties(fname="/mnt/c/Windows/Fonts/msmincho.ttc")

def create_plot(save_path):
    # 図のサイズ設定 (論文スタイルの横長長方形 5.6 x 4.4 インチ)
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    # データの定義 (2.5Å は速報値、5.0Å と 10.0Å は確定値)
    vac_thickness = [2.5, 5.0, 10.0]
    gamma_values = [2.470, 2.4485, 2.4488]

    # 1. データ点のプロット (線なし、見本画像 Fig.1 と同様の中抜き紫三角)
    ax.scatter(
        vac_thickness, 
        gamma_values, 
        color="#8A2BE2",        # 見本画像に合わせたパープル
        marker="^",             # 上向き三角
        s=70,                   # マーカーサイズ
        edgecolors="#8A2BE2", 
        linewidths=1.6,
        facecolors="none",      # 中抜き
        zorder=4
    )

    # 2. 文献値の水平点線 (3.03 J/m²)
    lit_value = 3.03
    ax.axhline(
        y=lit_value, 
        color="#222222", 
        linestyle="--", 
        linewidth=1.2, 
        zorder=3
    )

    # 文献値テキストの配置 (HPacker で日本語太字 + Times New Roman Bold をシームレス結合)
    font_lit_jp = fm.FontProperties(fname="/mnt/c/Windows/Fonts/msgothic.ttc", weight="bold", size=12)
    font_lit_en = fm.FontProperties(fname="/mnt/c/Windows/Fonts/timesbd.ttf", weight="bold", size=12.5)

    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_lit_jp, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_lit_en, color="#111111"))

    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=3)
    
    # 手書きスケッチに合わせて右上の点線直上に配置 (y=3.03 の少し上)
    y_norm = (lit_value / 5.0) + 0.024
    anchored_box = AnchoredOffsetbox(
        loc="lower right",
        child=packer,
        pad=0.0,
        frameon=False,
        bbox_to_anchor=(0.96, y_norm),
        bbox_transform=ax.transAxes
    )
    ax.add_artist(anchored_box)

    # 3. 軸範囲の設定
    ax.set_xlim(0.0, 16.0)
    ax.set_ylim(0.0, 5.0)

    # 4. 目盛りの設定 (目盛り数字はすべて本物の Times New Roman)
    font_tick = fm.FontProperties(fname="/mnt/c/Windows/Fonts/times.ttf", size=11.5)

    # 横軸目盛り: 0.0 〜 16.0 (2.0 刻み)
    x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    ax.set_xticks(x_ticks)
    # 「0.0は縦軸と同じだから表記は一つでいい」に従い、横軸の先頭は空文字にして縦軸と共用
    x_labels = ["" if x == 0.0 else f"{x:.1f}" for x in x_ticks]
    ax.set_xticklabels(x_labels, fontproperties=font_tick)

    # 縦軸目盛り: 0.0 〜 5.0 (1.0 刻み)
    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_tick)

    # 5. 軸ラベルの設定 (表題の文字サイズを 14.5pt に拡大、単位は Times New Roman / STIX)
    font_label = fm.FontProperties(fname="/mnt/c/Windows/Fonts/msgothic.ttc", size=14.5)

    # 横軸表題
    ax.set_xlabel(
        r"真空層の厚さ $\mathrm{[\AA]}$", 
        fontproperties=font_label, 
        labelpad=10
    )
    # 縦軸表題
    ax.set_ylabel(
        r"表面破壊エネルギー $\mathrm{[J/m^2]}$", 
        fontproperties=font_label, 
        labelpad=10
    )

    # 6. 学術論文スタイルの体裁 (見本画像 Fig.1 の忠実再現)
    # 四方の枠線 (box) を黒く明瞭に
    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.1)

    # 目盛り線を内向き (in) に、上下左右の4辺すべてに配置
    ax.tick_params(
        axis="both",
        which="major",
        direction="in",        # 内向き
        length=5.5,            # 目盛り線の長さ
        width=1.0,             # 目盛り線の太さ
        top=True,              # 上辺にも目盛り線
        right=True,            # 右辺にも目盛り線
        bottom=True,
        left=True,
        pad=6                  # 目盛り数字と軸の距離
    )

    # 背景色を完全な白に
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # レイアウトの自動調整
    plt.tight_layout()

    # 保存
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Updated graph saved successfully to {save_path}")

if __name__ == "__main__":
    out_file1 = "/home/yamazaki/mdi_workspace_backup/surface_energy_vs_vacuum_preview.png"
    out_file2 = "/home/yamazaki/.gemini/antigravity-ide/brain/1362d290-ff57-4721-b6d6-522994f3eca9/surface_energy_vs_vacuum_preview.png"
    create_plot(out_file1)
    create_plot(out_file2)
