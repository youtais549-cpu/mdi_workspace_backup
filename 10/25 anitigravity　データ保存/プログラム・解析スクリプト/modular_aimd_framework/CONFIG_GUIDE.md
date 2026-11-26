# 第一原理MD 表面破壊エネルギー計算：条件変更マニュアル (CONFIG GUIDE)

本フレームワークは、研究の進展に伴って**「頻繁に変更する研究条件（パラメータ）」** と **「一度構築したら触る必要のないシステム基盤（コアコード）」** を完全に分離し、毎回すべてのコードを見直すことなく、最小限の設定変更だけで安全かつ高速に計算を実行できるように設計されています。

---

## 1. ディレクトリ構造と役割分担

```text
modular_aimd_framework/
├── CONFIG_GUIDE.md               # 本マニュアル (条件変更の手順書)
│
├── parameters_variable/          # 【変わる部分: ユーザー編集対象】
│   ├── model_settings.py         # 結晶面、周期数(層数)、真空層厚さ、セル倍率の設定
│   ├── dft_settings.py           # カットオフエネルギー、k点、収束閾値などのDFT条件
│   ├── in.lammps.template        # 表面緩和(minimize) / AIMD(run) の切り替え
│   ├── generate_models.py        # 設定からスラブ・バルクモデル構造を一括自動生成
│   ├── calc_surface_energy.py    # E_slab と E_bulk から表面破壊エネルギー γ を自動算出
│   ├── fracture_metadata.json    # 断面積 2A や換算係数の自動生成メタデータ
│   ├── Si.upf, C.upf             # 擬ポテンシャルファイル
│   └── slab_*.data, bulk_*.data  # 自動生成されたLAMMPS構造データ
│
└── core_unchanging/              # 【変わらない部分: ユーザー編集不要】
    ├── qe_mdi_engine_core.py     # T4 GPU 最適化 MDI ソケット通信・ASE連成コアエンジン
    ├── master_run_gpu.sh         # Colabセットアップ & G:\マイドライブ\MD_backup 自動同期
    ├── run_colab_gpu.sh          # Colab上でのLAMMPS+QE並行起動スクリプト
    ├── make_xyz.py               # トラジェクトリ (dump) からアニメーションXYZへの変換
    └── workflow_cli.py           # ローカル側からSSH疎通・転送・監視を行うCLIツール
```

---

## 2. 条件変更時の対応一覧表

| 変更したい研究条件 | 編集するファイル | 変更する変数名 | 変更後の必要アクション |
| :--- | :--- | :--- | :--- |
| **① 真空層の厚さ** (例: 10Å $\to$ 15Å) | `parameters_variable/model_settings.py` | `VACUUM_THICKNESS` | `python3 generate_models.py` |
| **② 周期数 (スラブの厚さ・層数)** (例: 4層 $\to$ 6層 $\to$ 8層) | `parameters_variable/model_settings.py` | `N_PERIODS` | `python3 generate_models.py` |
| **③ 面内スーパーセルサイズ** (例: 3x3 $\to$ 4x4) | `parameters_variable/model_settings.py` | `SUPERCELL_XY` | `python3 generate_models.py` |
| **④ 亀裂を入れる結晶面** (例: {10-10} $\to$ {11-20}) | `parameters_variable/model_settings.py` | `CLEAVAGE_PLANE` | `python3 generate_models.py` |
| **⑤ DFT カットオフエネルギー** (例: 40 Ry $\to$ 50 Ry) | `parameters_variable/dft_settings.py` | `ecutwfc`, `ecutrho` | なし (エンジンが実行時に自動ロード) |
| **⑥ k点サンプリング** (例: Γ点 $\to$ 2x2x1) | `parameters_variable/dft_settings.py` | `kpts` | なし (エンジンが実行時に自動ロード) |
| **⑦ 計算モード切替** (表面緩和 vs 300K AIMD) | `parameters_variable/in.lammps.template` | `minimize` または `run` | コメントアウトの切り替え |

---

## 3. 各条件変更の具体的な手順と物理的注意点

### (1) 真空層の厚さを変える場合
* **ファイル**: `parameters_variable/model_settings.py`
  ```python
  VACUUM_THICKNESS = 15.0  # 10.0 から 15.0 Å に変更
  ```
* **反映コマンド**:
  ```bash
  python3 generate_models.py
  ```
* **物理的意味**:
  * スラブセルの高さ $L_z$ のみが拡張され、上下にそれぞれ指定した厚みの真空層が挿入されます。
  * **破面断面積 $A$（$L_x \times L_y$）およびバルク基準モデル（真空なし）には一切影響しません。**

### (2) 周期数（スラブの層数）を変える場合
* **ファイル**: `parameters_variable/model_settings.py`
  ```python
  N_PERIODS = 3  # 2周期(4層: 72原子) から 3周期(6層: 108原子) に変更
  ```
* **反映コマンド**:
  ```bash
  python3 generate_models.py
  ```
* **物理的意味**:
  * 表面破壊エネルギーの「スラブ厚さ収束性テスト」（厚さによって $\gamma$ が一定値に収束するか）を行う際に使用します。
  * `generate_models.py` を実行すると、**スラブモデルと全く同じ原子数（108原子など）のバルク基準モデルが自動的に再構築**され、「同じ大きさのケーキ同士の引き算（$\Delta E = E_{\text{slab}} - E_{\text{bulk}}$）」が完全に保証されます。

### (3) DFT パラメータを変更する場合
* **ファイル**: `parameters_variable/dft_settings.py`
  ```python
  DFT_CONFIG = {
      'ecutwfc': 50.0,       # 波動関数カットオフを 50 Ry に引き上げ
      'ecutrho': 400.0,      # 電荷密度カットオフ
      'conv_thr': 1.0e-5,    # 収束閾値
      'kpts': (2, 2, 1),     # スーパーセルが小さい場合に k点グリッドを指定
  }
  ```
* **反映コマンド**: なし
  * [qe_mdi_engine_core.py](file:///home/yamazaki/mdi_workspace_backup/modular_aimd_framework/core_unchanging/qe_mdi_engine_core.py) が実行時に本ファイルを動的にインポートするため、コアエンジンの再編集は不要です。

### (4) 計算モード（表面構造緩和 vs 有限温度AIMD）を切り替える場合
* **ファイル**: `parameters_variable/in.lammps.template`
  * **表面破壊エネルギー評価（基底状態）**:
    `minimize 0.0 1.0e-3 100 1000` を有効化。
  * **有限温度 AIMD（熱揺らぎ・動的再構成）**:
    `minimize` を `#` でコメントアウトし、`velocity` と `fix 2 all nve` を有効化。

---

## 4. 計算後の表面破壊エネルギー $\gamma$ 自動算出

スラブ計算（$E_{\text{slab}}$）およびバルク基準計算（$E_{\text{bulk}}$）が終了したら、以下のコマンドを実行します：

```bash
cd parameters_variable
python3 calc_surface_energy.py <E_slab> <E_bulk>
# 例: python3 calc_surface_energy.py -10500.25 -10539.75
```

* `fracture_metadata.json` から断面積 $2A$ と換算係数 $16.021766$ を自動取得し、
  $$\gamma [\text{J/m}^2] = \frac{E_{\text{slab}} - E_{\text{bulk}}}{2A} \times 16.021766$$
  を即座に計算して、先行研究（Rauls et al. 1999 の $2.27\text{ J/m}^2$）との比較判定を出力します。
