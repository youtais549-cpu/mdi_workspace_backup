# 2H-SiC {10-10} 300K NVT 第一原理分子動力学 (AIMD) ガイド

本ディレクトリは、72原子 2H-SiC $\{10\bar{1}0\}$ スラブモデル（真空層 各10Å）を対象とした、**常温（300K）NVT アンサンブル第一原理分子動力学（AIMD）** の実行環境です。

1回目の 0K 構造緩和計算（`results_SiC_10-10_slab_relaxed`）とは完全に独立したディレクトリとして構成されています。

---

## 1. ファイル構成
- [`in.lammps`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/in.lammps): 300K NVT AIMD 用の LAMMPS 入力スクリプト
- [`run_aimd_nvt_gpu.sh`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/run_aimd_nvt_gpu.sh): Colab T4 GPU 上での MDI ワンタッチ起動スクリプト
- [`slab_10-10_relaxed.data`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/slab_10-10_relaxed.data): **（推奨初期構造）** 1回目の 0K 構造緩和完了後の最安定構造
- [`slab_10-10_unrelaxed.data`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/slab_10-10_unrelaxed.data): 理想切断直後の未緩和構造
- [`qe_mdi_engine_gpu.py`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/qe_mdi_engine_gpu.py): Quantum ESPRESSO GPU 連成エンジン
- [`make_xyz.py`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/make_xyz.py): Winmostar アニメーション用 XYZ 変換ツール
- `C.upf`, `Si.upf`: PAW 擬ポテンシャルファイル

---

## 2. NVT 第一原理MDで設定すべき重要項目

有限温度（300K）MDを行うにあたり、静的な構造緩和（0K）とは異なり、以下の項目を厳密に設定する必要があります（すべて [`in.lammps`](file:///home/yamazaki/mdi_workspace_backup/aimd_nvt_300K_vac10A/in.lammps) に設定済みです）：

### ① 初期構造の選択（緩和後 vs 未緩和）
- **推奨**: `slab_10-10_relaxed.data`（0K 緩和済み構造）からスタート。
- **理由**: 未緩和の理想切断構造は表面に大きな不釣り合い力（$F_{\max} \approx 2.55\text{ eV/\AA}$）が残っているため、いきなり 300K の熱運動を与えると原子が急激に跳ね上がり、非物理的な結合切断や電子状態 SCF の発散を招くリスクがあります。事前に 0K で極小点に落ち着かせた構造から熱を与えるのが第一原理MDの標準プロトコルです。

### ② タイムステップ（Time step, `timestep`）
- **設定値**: `0.001 ps`（$1.0\text{ fs}$）
- **理由**: SiC の結晶格子振動（光学フォノン）の最高振動数は約 $1000\text{ cm}^{-1}$（周期 約 $33\text{ fs}$）です。運動方程式の安定な数値積分には、周期の 1/20〜1/30 以下の時間刻みが必要となるため、$1.0\text{ fs}$ が最適です。

### ③ サーモスタットの緩和時間（`Tdamp`）
- **設定値**: `fix 2 all nvt temp 300.0 300.0 0.1`（$T_{\text{damp}} = 0.1\text{ ps} = 100\text{ fs}$）
- **理由**: Nosé-Hoover サーモスタットの温度緩和時間は、LAMMPS 公式の推奨として「タイムステップの100倍（$100 \times \Delta t$）」とされています。短すぎると不自然な高周波温度振動を生み、長すぎると 300K への温度追従が極めて遅くなります。

### ④ 初期熱速度と重心ドリフト防止
- **設定値**: 
  - `velocity all create 300.0 <seed> mom yes rot yes dist gaussian`
  - `fix 3 all momentum 50 linear 1 1 1`
- **理由**: スラブモデルは $z$ 方向に真空層があるため、熱振動の微小な非対称性によってスラブ全体が宇宙船のように一定速度で真空層中を平行移動（ドリフト）してしまいます。これを防ぐため、初期速度生成時に並進運動量をゼロ化し、さらに 50 ステップごとに重心並進速度をリセットします。

---

## 3. 計算コストとシミュレーション時間の目安 (Tesla T4 GPU)

1 ステップ（$1.0\text{ fs}$）ごとに Quantum ESPRESSO GPU による SCF 計算が実行されます：

| ステップ数 | シミュレーション時間 | 所要時間の目安 (T4 GPU) | 目的 |
| :--- | :--- | :--- | :--- |
| **100 steps** | $100\text{ fs}$ ($0.1\text{ ps}$) | 約 30 〜 40 分 | 動作確認・初期熱平衡化の立ち上がり確認 |
| **500 steps** | $500\text{ fs}$ ($0.5\text{ ps}$) | 約 2.5 〜 3 時間 | 熱平衡化（300K定常状態への到達） |
| **1,000 steps** | $1,000\text{ fs}$ ($1.0\text{ ps}$) | 約 5 〜 6 時間 | 定常状態での表面熱振動・熱的再構成のサンプリング |

---

## 4. 実行手順（実行する準備が整った段階で実施）

1. Colab 環境へ本ディレクトリをアップロード（または転送）
2. 以下のコマンドでバックグラウンド実行:
   ```bash
   bash run_aimd_nvt_gpu.sh
   ```
3. 完了後、自動生成される `md_nvt_animation.xyz` を Winmostar に読み込ませることで、常温で表面原子が熱振動する様子をアニメーション再生できます。
