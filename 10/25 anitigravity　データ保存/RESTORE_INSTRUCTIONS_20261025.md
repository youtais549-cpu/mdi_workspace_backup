# 2H-SiC AIMD/MDI プロジェクト：環境構築およびデータ復旧指示書 (2026-10-25)

本ドキュメントは、パソコン修理完了後の新環境（または初期化された Antigravity IDE）において、本研究の全環境・学習済みルール・計算成果物を 100% 確実に復元するための指示書です。

---

## 1. バックアップフォルダの構造

保存先フォルダ: `10/25 anitigravity　データ保存/`

```
10/25 anitigravity　データ保存/
├── 環境構築およびデータ復旧指示書.txt       # テキスト形式の復旧指示書（文字化けのないプレーンテキスト）
├── RESTORE_INSTRUCTIONS_20261025.md       # 本ドキュメント（Markdown形式）
├── 会話ログ/
│   ├── 会話ログ_全履歴_20261025.txt      # 代替機におけるAI（Antigravity）との全会話テキスト（完全版）
│   └── raw_transcripts/                   # IDE復元用 JSONL トランスクリプト群
├── 学習内容と運用ルール/
│   ├── AGENTS.md                          # 最新の恒久ルール（全10章・最重要）
│   ├── GRAPH_STYLE_SPEC.md                # 論文・ポスター・Word用グラフ体裁仕様書
│   ├── RELAXATION_GRAPH_PROTOCOL.json     # 3種推移グラフ自動生成指示書プロトコル
│   ├── 学習内容と知見の全体総括.md        # 全学習知見（v1〜v9）の体系的解説
│   ├── 学習プロポーザル全世代集（v1〜v9）/  # 過去の承認プロポーザル全世代アーカイブ
│   └── 個別運用ルール群/                  # .agents/rules/ 配下の各専門ルール（7種）
├── 計算成果物・解析データ・グラフ/
│   ├── SURFACE_ENERGY_RESULTS.md          # 表面破壊エネルギー総合計算台帳
│   ├── surface_energy_results.csv         # 全条件の計算結果CSVデータベース
│   ├── 周期数と表面破壊エネルギーの関係.*  # ポスター・発表用完成グラフ（PNG, PDF, SVG）
│   ├── 周期数と表面破壊エネルギーの関係_word_8cm.* # Word最適化グラフ（PNG, PDF, SVG）
│   └── 各種真空層依存性比較グラフ群
├── 各条件の計算ディレクトリ/
│   ├── calc_2H-SiC_10-10_2periods_vac2.5A_2nd/            # 2周期2.5Å 2回目（最適化収束基準・自然収束達成）
│   ├── calc_2H-SiC_10-10_4periods_vac5A_natural_cleavage/ # 4周期5Å 自然へき開スラブ
│   ├── calc_2H-SiC_10-10_6periods_vac5A_natural_cleavage/ # 6周期5Å 自然へき開スラブ
│   ├── 各バルクSCF計算ディレクトリ（72, 144, 216原子）
│   └── 各種緩和結果ディレクトリ群（全入出力、espresso.pwo, log.lammps, 3種グラフ等）
├── プログラム・解析スクリプト/
│   ├── auto_generate_progression_graphs.py                # 3種推移グラフ自動生成エンジン
│   ├── generate_surface_energy_vs_periods_graph.py        # 周期数比較グラフ作成スクリプト
│   ├── generate_word_standard_progression_graphs.py        # Word用グラフ作成スクリプト
│   ├── modular_aimd_framework/                            # 自動解析・エネルギー計算モジュール
│   └── research_simulations/                              # モデル作成スクリプト・CIF・XYZ・DATA
└── 環境設定・フォント/
    ├── conda_environment.yml              # Python (Conda) 仮想環境定義ファイル
    ├── msmincho.ttc                       # MS明朝フォント（文字化け防止）
    ├── times.ttf                          # Times New Roman フォント
    └── ssh_config_backup.txt              # Colab SSH 接続設定バックアップ
```

---

## 2. 環境復元の手順

### Step 1: GitHub からリポジトリを取得
```bash
git clone https://github.com/youtais549-cpu/mdi_workspace_backup.git
cd mdi_workspace_backup
```
※前回のデータと混ざらないよう、直近の作業データはすべて `10/25 anitigravity　データ保存/` に隔離・保管されています。

### Step 2: Python / Conda 環境の構築
```bash
conda env create -f "10/25 anitigravity　データ保存/環境設定・フォント/conda_environment.yml"
conda activate mdi_env
```
または既存環境に必要なパッケージをインストール：
```bash
pip install ase pymdi numpy scipy matplotlib
```
フォントファイル（`msmincho.ttc`, `times.ttf`）を `~/.fonts/` に配置してください。

### Step 3: Antigravity IDE へのルール・記憶の復元（最重要）
1. `10/25 anitigravity　データ保存/学習内容と運用ルール/AGENTS.md` をワークスペース直下に配置します。
2. `個別運用ルール群/` を `.agents/rules/` に配置します。
3. `RELAXATION_GRAPH_PROTOCOL.json` をワークスペース直下に配置します。

> [!NOTE]
> これにより、Antigravity IDE は初回起動時から「文献値 3.03 J/m²」「粗結合切断の物理的前提」「最適化収束基準」「先行バルクSCF確定」等の全ルールを完全に認識した状態でペアプログラミングを開始できます。AIに「AGENTS.md を読み込んで作業を継続して」と伝えるだけで完璧に引き継がれます。

### Step 4: Google Colab (Tesla T4 GPU) 接続の復旧
1. お手持ちの SSH 鍵（`id_ed25519`）を `~/.ssh/id_ed25519` に配置し、パーミッションを設定：
   ```bash
   chmod 600 ~/.ssh/id_ed25519
   ```
2. Colab ノートブックを起動し、トンネル URL とポート番号を確認して `~/.ssh/config` に反映。
3. `ssh colab` でワンタッチ接続可能です。

---

## 3. 確定した計算結果台帳

| モデル | 原子数 | 真空厚 | スラブ全エネルギー $E_{\text{slab}}$ [eV] | バルク基準全エネルギー $E_{\text{bulk}}$ [eV] | 表面破壊エネルギー $\gamma$ [$\text{J/m}^2$] | 文献値比 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2周期・真空10.0 Å** | 72 | 10.0 Å | -31,892.6375 | -31,935.3562 | **2.4488** | 80.8% |
| **2周期・真空5.0 Å** | 72 | 5.0 Å | -31,892.6430 | -31,935.3562 | **2.4485** | 80.8% |
| **2周期・真空2.5 Å (2回目・自然収束)** | 72 | 2.5 Å | -31,892.2525 | -31,935.3562 | **2.4709** | 81.5% |
| **4周期・真空5.0 Å (自然へき開)** | 144 | 5.0 Å | -63,829.4705 | -63,870.7107 | **2.3642** | 78.0% |
| **6周期・真空5.0 Å (自然へき開)** | 216 | 5.0 Å | -95,765.4880 | -95,806.2608 | **2.3366** | 77.1% |
| **文献値（Rauls et al. 1999 p.462）** | - | - | - | - | **3.0300** | 100.0% |
