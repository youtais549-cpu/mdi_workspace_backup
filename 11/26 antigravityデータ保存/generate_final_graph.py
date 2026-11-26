#!/usr/bin/env python3
"""
generate_final_graph.py
2H-SiC {10-10} 表面破壊エネルギーの真空層厚さ依存性 最終グラフ生成スクリプト
(研究概要 Word 文書・横幅 8.0 cm 配置用 最適化版)

【修正の目的と設計仕様】
1. Word 文書 (本文: MS明朝 10.5 pt、Fig. 1 と横並び配置、掲載幅約 8.0 cm) に完全対応。
2. 物理寸法: 横 8.0 cm × 縦 6.2 cm (Word 上で 100% 表示・拡大縮小不要)。
   ※ 自動余白調整 (bbox_inches='tight') を無効化し、指定物理寸法 (8.0 cm × 6.2 cm) を厳格に保持。
3. フォント仕様:
   - 軸ラベル: MS明朝 10.5 pt
   - 目盛り数字: Times New Roman 9.5 pt (整数表示)
   - 文献値日本語: MS明朝 Bold 9.5 pt
   - 文献値英数字・単位: Times New Roman Bold 9.5 pt
   - 数式部分: STIX (Times New Roman 互換)
4. 出力形式 (全 3 形式):
   - SVG: 文字アウトライン化 (svg.fonttype = 'path') により Word 貼付時のフォント置換・文字化けを完全防止
   - PNG: 600 dpi の高解像度ラスター画像
   - PDF: 学術出版対応ベクター形式
5. 表示範囲とバリエーション:
   - 16 Å 版 (標準): 横軸 0～16 Å, 縦軸 0～5 J/m²
   - 12 Å 版 (比較検討案): 横軸 0～12 Å, 縦軸 0～5 J/m² (データ点間隔を広げ視認性を向上)
"""

import os
import sys
import csv
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, TextArea

# 数式フォントに STIX (Times New Roman 互換) を適用
plt.rcParams['mathtext.fontset'] = 'stix'
# SVG 出力時に文字をパス (アウトライン) 化して Word での文字化け・フォント置換を防止
plt.rcParams['svg.fonttype'] = 'path'

CSV_PATH = "/home/yamazaki/mdi_workspace_backup/surface_energy_results.csv"
PLOT_DATA_CSV = "/home/yamazaki/mdi_workspace_backup/surface_energy_vs_vacuum_plot_data.csv"
DESKTOP_DIR = "/mnt/c/Users/S015/OneDrive - YNU(ynu.jp)/デスクトップ"
POSTER_DIR = "/mnt/c/Users/S015/OneDrive - YNU(ynu.jp)/4/研究室/ポスター発表"

def get_font_properties():
    """Windows フォント (MS明朝, Times New Roman) のパスを解決"""
    win_fonts = "/mnt/c/Windows/Fonts"
    msmincho_path = os.path.join(win_fonts, "msmincho.ttc")
    times_path = os.path.join(win_fonts, "times.ttf")
    timesbd_path = os.path.join(win_fonts, "timesbd.ttf")

    if not os.path.exists(msmincho_path):
        msmincho_path = None
    if not os.path.exists(times_path):
        times_path = None
    if not os.path.exists(timesbd_path):
        timesbd_path = None

    font_mincho_label = fm.FontProperties(fname=msmincho_path, size=10.5)
    font_mincho_lit = fm.FontProperties(fname=msmincho_path, weight="bold", size=9.5)
    font_times_tick = fm.FontProperties(fname=times_path, size=9.5)
    font_times_lit = fm.FontProperties(fname=timesbd_path, weight="bold", size=9.5)

    return font_mincho_label, font_mincho_lit, font_times_tick, font_times_lit

def load_data():
    """CSV から計算値を取得 (取得できない場合は確定した厳密な第一原理計算値をフォールバック使用)"""
    gamma_2_5 = 2.4703
    gamma_5_0 = 2.4485
    gamma_10_0 = 2.4488

    # 1. 専用プロット CSV から読み込み試行
    if os.path.exists(PLOT_DATA_CSV):
        try:
            with open(PLOT_DATA_CSV, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    vac = float(row['Vacuum_Thickness_Angstrom'])
                    g = float(row['Surface_Fracture_Energy_J_m2'])
                    if abs(vac - 2.5) < 0.1: gamma_2_5 = g
                    elif abs(vac - 5.0) < 0.1: gamma_5_0 = g
                    elif abs(vac - 10.0) < 0.1: gamma_10_0 = g
            return gamma_2_5, gamma_5_0, gamma_10_0
        except Exception as e:
            print(f"Notice: Failed to read from {PLOT_DATA_CSV}: {e}")

    # 2. 総合計算 CSV から読み込み試行
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if '10-10' in row.get('Plane', ''):
                        vac = float(row['Vacuum_Angstrom'])
                        g = float(row['Gamma_J_m2'])
                        if abs(vac - 2.5) < 0.1: gamma_2_5 = g
                        elif abs(vac - 5.0) < 0.1: gamma_5_0 = g
                        elif abs(vac - 10.0) < 0.1: gamma_10_0 = g
        except Exception as e:
            print(f"Notice: Failed to read from {CSV_PATH}: {e}")

    return gamma_2_5, gamma_5_0, gamma_10_0

def generate_single_plot(x_max=16.0, suffix="16A", copy_desktop=True):
    """
    指定された横軸最大値 (x_max) で Word 最適化グラフを生成
    - x_max = 16.0: 基本の 0～16 Å 表示
    - x_max = 12.0: 比較検討案の 0～12 Å 表示
    """
    gamma_2_5, gamma_5_0, gamma_10_0 = load_data()
    font_mincho_label, font_mincho_lit, font_times_tick, font_times_lit = get_font_properties()

    # 1. 物理寸法の厳格設定 (横 8.0 cm × 縦 6.2 cm)
    width_cm = 8.0
    height_cm = 6.2
    w_in = width_cm / 2.54
    h_in = height_cm / 2.54

    fig, ax = plt.subplots(figsize=(w_in, h_in), dpi=600)
    # プロット領域を最大化しつつ、軸ラベルや単位の端切れを防止する精密余白配分
    fig.subplots_adjust(left=0.21, right=0.94, bottom=0.20, top=0.96)

    # 2. データ点のプロット (紫色中抜き三角マーカー, 線なし)
    vac_thickness = [2.5, 5.0, 10.0]
    gamma_values = [gamma_2_5, gamma_5_0, gamma_10_0]

    ax.scatter(
        vac_thickness, 
        gamma_values, 
        color="#8A2BE2", 
        marker="^", 
        s=45, 
        linewidths=1.3, 
        facecolors="none", 
        zorder=4
    )

    # 3. 文献値の水平破線 (3.03 J/m²)
    lit_value = 3.03
    ax.axhline(y=lit_value, color="#222222", linestyle="--", linewidth=1.0, zorder=3)

    # 文献値テキスト (MS明朝 9.5 pt + Times New Roman Bold 9.5 pt を横並び配置)
    area_jp = TextArea("文献値", textprops=dict(fontproperties=font_mincho_lit, color="#111111"))
    area_en = TextArea("(3.03 J/m²)", textprops=dict(fontproperties=font_times_lit, color="#111111"))
    packer = HPacker(children=[area_jp, area_en], align="baseline", pad=0, sep=2)

    # y=3.03 の破線直上に配置 (ylim 0～5 に対する正規化座標)
    y_norm = (lit_value / 5.0) + 0.026
    anchored_box = AnchoredOffsetbox(
        loc="lower right", 
        child=packer, 
        pad=0.0, 
        frameon=False,
        bbox_to_anchor=(0.95, y_norm), 
        bbox_transform=ax.transAxes
    )
    ax.add_artist(anchored_box)

    # 4. 表示範囲の設定
    ax.set_xlim(0.0, x_max)
    ax.set_ylim(0.0, 5.0)

    # 5. 目盛り設定 (小数点第一位表示, Times New Roman 9.5 pt)
    if abs(x_max - 16.0) < 0.1:
        x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    else:
        x_ticks = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0]

    ax.set_xticks(x_ticks)
    # 原点 0.0 は縦軸と重なるため非表示、それ以外は小数点第一位表示 (2.0, 4.0, 14.0 など)
    ax.set_xticklabels(["" if x == 0.0 else f"{x:.1f}" for x in x_ticks], fontproperties=font_times_tick)

    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{y:.1f}" for y in y_ticks], fontproperties=font_times_tick)

    # 6. 軸ラベルの設定 (MS明朝 10.5 pt, 単位は STIX / Times 互換セリフ体)
    ax.set_xlabel(r"真空層の厚さ $\mathrm{[\AA]}$", fontproperties=font_mincho_label, labelpad=3)
    ax.set_ylabel(r"表面破壊エネルギー $\mathrm{[J/m^2]}$", fontproperties=font_mincho_label, labelpad=4)

    # 7. 枠線および目盛り線のスタイル
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

    # 背景色設定
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # 8. ファイル出力 (SVG, PNG 600dpi, PDF)
    # ※ bbox_inches="tight" を使わずに出力することで、Word で 100% 貼付時に指定寸法 (8.0 cm × 6.2 cm) を保持
    base_name = f"surface_energy_vs_vacuum_word_{suffix}"
    out_png = f"/home/yamazaki/mdi_workspace_backup/{base_name}.png"
    out_svg = f"/home/yamazaki/mdi_workspace_backup/{base_name}.svg"
    out_pdf = f"/home/yamazaki/mdi_workspace_backup/{base_name}.pdf"

    plt.savefig(out_png, dpi=600)
    plt.savefig(out_svg)
    plt.savefig(out_pdf)

    # 16A の場合は標準ファイル名 (surface_energy_vs_vacuum_final.*) にも保存
    if suffix == "16A":
        final_png = "/home/yamazaki/mdi_workspace_backup/surface_energy_vs_vacuum_final.png"
        final_svg = "/home/yamazaki/mdi_workspace_backup/surface_energy_vs_vacuum_final.svg"
        final_pdf = "/home/yamazaki/mdi_workspace_backup/surface_energy_vs_vacuum_final.pdf"
        plt.savefig(final_png, dpi=600)
        plt.savefig(final_svg)
        plt.savefig(final_pdf)

    plt.close()

    print(f"✅ [{suffix}] 生成完了:")
    print(f"   PNG (600 dpi) : {out_png}")
    print(f"   SVG (アウトライン): {out_svg}")
    print(f"   PDF (ベクター) : {out_pdf}")

    # 9. Windows デスクトップおよび研究室ポスター発表フォルダへのコピー
    target_dirs = []
    if os.path.exists(DESKTOP_DIR):
        target_dirs.append(("デスクトップ", DESKTOP_DIR))
    if os.path.exists(POSTER_DIR):
        target_dirs.append(("研究室ポスター発表", POSTER_DIR))

    if copy_desktop:
        for dir_label, target_dir in target_dirs:
            try:
                for src, ext in [(out_png, ".png"), (out_svg, ".svg"), (out_pdf, ".pdf")]:
                    dst = os.path.join(target_dir, f"{base_name}{ext}")
                    shutil.copy2(src, dst)
                if suffix == "16A":
                    for src_name in ["surface_energy_vs_vacuum_final.png",
                                     "surface_energy_vs_vacuum_final.svg",
                                     "surface_energy_vs_vacuum_final.pdf"]:
                        shutil.copy2(os.path.join("/home/yamazaki/mdi_workspace_backup", src_name),
                                     os.path.join(target_dir, src_name))
                print(f"   📋 {dir_label} フォルダにコピー完了")
            except Exception as e:
                print(f"   Notice: {dir_label} へのコピー失敗: {e}")

def main():
    print("=" * 60)
    print("2H-SiC 表面破壊エネルギー グラフ生成 (Word 8.0 cm 最適化版)")
    print("=" * 60)
    
    # 16 Å 版 (標準) の生成
    generate_single_plot(x_max=16.0, suffix="16A", copy_desktop=True)

    # 12 Å 版 (比較検討案) の生成
    generate_single_plot(x_max=12.0, suffix="12A", copy_desktop=True)

    print("=" * 60)
    print("すべての形式 (SVG / PNG 600dpi / PDF) の出力が正常に完了しました。")
    print("=" * 60)

if __name__ == "__main__":
    main()
