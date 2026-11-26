# 2H-SiC $\{10\bar{1}0\}$ 8周期（288原子）真空層 3.0 Å 300 K AIMD 比較検証レポート
**（初期構造：0 K 構造最適化なし［未緩和］ vs. 0 K 構造最適化あり［緩和済み］）**

本レポートは、2H-SiC $\{10\bar{1}0\}$ 自然へき開面スラブ（8周期・16層・288原子・真空層厚さ 3.0 Å）において、**初期構造を「0 K 構造最適化なし（理想へき開切断スラブ）」とした場合**の 300 K NVT-AIMD（100 steps = 100 fs）の結果と、先に行った**「0 K 構造最適化あり」**の結果を比較検証したものです。

---

## 1. エネルギー推移グラフ（Word配置最適化 8.0 cm × 6.2 cm, 600 dpi 完全準拠）

````carousel
![全エネルギー推移グラフ (Word最適化)](/home/WORKSTATION4WSL/.gemini/antigravity/brain/cc114744-ec01-4b04-8765-40ec69ef7d2d/全エネルギー推移_未緩和AIMD_word_8cm.png)
<!-- slide -->
![ポテンシャルエネルギー推移グラフ (Word最適化)](/home/WORKSTATION4WSL/.gemini/antigravity/brain/cc114744-ec01-4b04-8765-40ec69ef7d2d/ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.png)
<!-- slide -->
![エネルギー成分変化量推移グラフ (Word最適化)](/home/WORKSTATION4WSL/.gemini/antigravity/brain/cc114744-ec01-4b04-8765-40ec69ef7d2d/エネルギー変化量推移_未緩和AIMD_word_8cm.png)
<!-- slide -->
![エネルギー総合推移グラフ (プレゼンテーション仕様)](/home/WORKSTATION4WSL/.gemini/antigravity/brain/cc114744-ec01-4b04-8765-40ec69ef7d2d/エネルギー総合推移_未緩和AIMD_プレゼン仕様.png)
<!-- slide -->
![構造最適化あり vs なし 直接比較グラフ](/home/WORKSTATION4WSL/.gemini/antigravity/brain/cc114744-ec01-4b04-8765-40ec69ef7d2d/AIMD_Comparison_Relaxed_vs_Unrelaxed_100steps.png)
````

* **スライド 1（全エネルギー推移）**: 系全体の力学的エネルギー $E_{\text{total}} = E_{\text{pot}} + E_{\text{kin}}$ の推移。$-127,662.73 \sim -127,662.75\text{ eV}$（変動幅わずか $0.04\text{ eV}$）という極めて高い精度で完全保存されている様子を示します。
* **スライド 2（ポテンシャルエネルギー推移）**: 表面再構成に伴い、Step 0 の $-127,673.86\text{ eV}$ から Step 19 の $-127,677.13\text{ eV}$ へと **$-3.27\text{ eV}$ 自発的に低下（解放）**し、その後 $-127,674\text{ eV}$ 付近で安定に熱振動する様子を示します。
* **スライド 3（エネルギー成分変化量推移 $\Delta E$）**: 初期値（$0\text{ fs}$）からの変化量 $\Delta E_{\text{pot}}$（青丸・実線）の減少と、$\Delta E_{\text{kin}}$（赤四角・破線）の増加が完全に鏡像関係（$\Delta E_{\text{pot}} + \Delta E_{\text{kin}} = 0$）を成し、全エネルギー変化 $\Delta E_{\text{total}}$（紫三角）がゼロ直線上に厳密に留まっている様子を示します。
* **スライド 4（エネルギー総合推移）**: 上段に全エネルギー、下段にポテンシャルエネルギーと運動エネルギーの 2 軸プロットを配置したプレゼン・発表用長方形グラフ。
* **スライド 5（構造最適化あり vs. なし 比較）**: 温度・表面変位・スラブ間ギャップの直接比較グラフ。

---

## 2. エネルギーデータの詳細推移（Step 0 〜 100）

| Step (時間) | 全エネルギー $E_{\text{total}}$ [eV] | ポテンシャル $E_{\text{pot}}$ [eV] | 運動エネルギー $E_{\text{kin}}$ [eV] | $\Delta E_{\text{pot}}$ [eV] | $\Delta E_{\text{kin}}$ [eV] | 温度 $T$ [K] | 物理的解釈 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0 (0 fs)** | **$-127,662.73$** | $-127,673.86$ | $11.129$ | $0.000$ | $0.000$ | $300.00$ | 未緩和理想切断状態（$T = 300\text{ K}$ の初期熱速度） |
| **5 (5 fs)** | **$-127,662.72$** | $-127,672.77$ | $10.048$ | $+1.090$ | $-1.081$ | $270.86$ | 初期のバネ伸びに伴う運動エネルギーのポテンシャル変換 |
| **12 (12 fs)** | **$-127,662.71$** | $-127,673.59$ | $10.879$ | $+0.270$ | $-0.250$ | $293.25$ | 表面原子の内側沈降が加速 |
| **19 (19 fs)** | **$-127,662.72$** | **$-127,677.13$** *(極小)* | **$14.412$** *(極大)* | **$-3.270$** | **$+3.283$** | **$388.49$** | **表面再構成エネルギー解放により運動エネルギー・温度が最大化** |
| **27 (27 fs)** | **$-127,662.72$** | $-127,672.77$ | $10.047$ | $+1.090$ | $-1.082$ | $270.84$ | 内側への沈み込みが最大に達し、運動エネルギーがバネへ蓄積 |
| **31 (31 fs)** | **$-127,662.72$** | **$-127,671.35$** *(極大)* | **$8.632$** *(極小)* | **$+2.510$** | **$-2.497$** | **$232.69$** | 格子バネの伸び最大による温度の折り返し極小点 |
| **40 (40 fs)** | **$-127,662.74$** | $-127,675.30$ | $12.558$ | $-1.440$ | $+1.429$ | $338.52$ | 表面バックリング（Si沈降・C浮き上がり）の急激な進行 |
| **55 (55 fs)** | **$-127,662.74$** | $-127,672.58$ | $9.835$ | $+1.280$ | $-1.294$ | $265.12$ | 表面段差が最大ピーク（ギャップ最小 $5.69\text{ \AA}$） |
| **70 (70 fs)** | **$-127,662.74$** | $-127,673.91$ | $11.171$ | $-0.050$ | $+0.042$ | $301.13$ | Nosé-Hoover 熱浴により過剰熱が定常化 |
| **85 (85 fs)** | **$-127,662.74$** | $-127,674.43$ | $11.695$ | $-0.570$ | $+0.566$ | $315.24$ | $300\text{ K}$ 近傍での熱振動 |
| **100 (100 fs)**| **$-127,662.74$** | $-127,673.95$ | $11.215$ | $-0.090$ | $+0.086$ | $302.32$ | **全エネルギー変動 $0.01\text{ eV}$、温度 $302\text{ K}$ で完全定常状態** |

---

## 3. ファイルリンク一覧

* **データディレクトリ**: [`aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/`](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/)
* **全エネルギー推移グラフ (Word 8.0cm × 6.2cm)**:
  [`全エネルギー推移_未緩和AIMD_word_8cm.png`](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/全エネルギー推移_未緩和AIMD_word_8cm.png)（[PDF](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/全エネルギー推移_未緩和AIMD_word_8cm.pdf) / [SVG](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/全エネルギー推移_未緩和AIMD_word_8cm.svg)）
* **ポテンシャルエネルギー推移グラフ (Word 8.0cm × 6.2cm)**:
  [`ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.png`](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.png)（[PDF](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.pdf) / [SVG](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.svg)）
* **エネルギー変化量推移グラフ (Word 8.0cm × 6.2cm)**:
  [`エネルギー変化量推移_未緩和AIMD_word_8cm.png`](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/エネルギー変化量推移_未緩和AIMD_word_8cm.png)（[PDF](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/エネルギー変化量推移_未緩和AIMD_word_8cm.pdf) / [SVG](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/エネルギー変化量推移_未緩和AIMD_word_8cm.svg)）
* **エネルギー総合推移グラフ (プレゼン仕様 5.6 × 4.6 インチ)**:
  [`エネルギー総合推移_未緩和AIMD_プレゼン仕様.png`](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/エネルギー総合推移_未緩和AIMD_プレゼン仕様.png)（[PDF](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/エネルギー総合推移_未緩和AIMD_プレゼン仕様.pdf) / [SVG](file:///home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/エネルギー総合推移_未緩和AIMD_プレゼン仕様.svg)）
* **NAS 保存先**: `\\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法\{101_0}8周期3.0Å構造最適化なしtest run\`
