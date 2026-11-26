# MDI Workspace Core Rules & Agent Guidelines

本ワークスペースは、2H-SiC の第一原理分子動力学 (AIMD) および構造緩和・表面破壊エネルギー計算（MDI: LAMMPS + Quantum ESPRESSO GPU）を行うプロジェクトです。

エージェントは以下のルールを厳守してください。

---

## 1. 計算結果の上書き防止と個別アーカイブ（最重要・絶対遵守）
- **直接上書き・一括削除の禁止**:
  `dump.lammpstrj`, `espresso.pwo`, `md_animation.xyz`, `log.lammps`, `qe_engine.log` 等の計算出力ファイルを、後続の別計算（バルク基準計算、他の方位、異なるカットオフ等）によって直接上書きしたり、スクリプトの `rm -rf` で安易に削除することは**絶対禁止**です。
- **個別退避ディレクトリの作成**:
  計算完了時、または新しい計算を同一環境で開始する前には、必ずモデル名・面方位・計算種別・日付を付与した独立ディレクトリ（例: `2H-SiC_10-10_slab_relaxed_YYYYMMDD/`）を Google Drive（`G:\マイドライブ\MD_backup\`）およびローカル（`mdi_workspace_backup/`）に作成し、すべての成果物を完全退避・保護してください。**ユーザーからバックアップ先フォルダ名（全角スペース、波括弧、試行回数等）が指定された場合はその指定を厳格に順守し、Colab 側の同期ループを即座に新パスへ向け替えること**。
- **アーカイブ済みの計算成果**:
  - `2H-SiC_10-10_slab_relaxed_20261020/`: 72原子 2H-SiC $\{10\bar{1}0\}$ スラブの CG 構造緩和計算（$E_{\text{slab}} = -31,892.6375\text{ eV}$、$F_{\max} \le 3.9\times 10^{-4}\text{ eV/\AA}$）。永続保存済み。
  - `2H-SiC_10-10_bulk_scf_20261020/`: 72原子 2H-SiC $\{10\bar{1}0\}$ バルク基準モデルの QE GPU 単独 1点 SCF 計算（$E_{\text{bulk}} = -31,935.3562\text{ eV}$、$F_{\text{total}} = 0.0567\text{ Ry/au}$）。永続保存済み。
  - **表面破壊エネルギー算出結果（検証完了）**:
    $\Delta E = 42.7187\text{ eV}$, $2A = 279.4977\text{ \AA}^2 \implies \mathbf{\gamma = 2.4488\text{ J/m}^2}$（Rauls et al. 1999 の文献値 $2.27 \sim 2.44\text{ J/m}^2$ と極めて高い精度で一致）。
- **スラブ緩和計算前の「バルク 1 点 SCF 先行確定」プロトコル（必須順序）**:
  新しい条件（周期数拡張など）でスラブ構造緩和計算を開始する前に、**必ず同一原子数の真のバルクモデル（真空層 0 Å）による Quantum ESPRESSO GPU 1 点 SCF 計算を先行実施**すること。
  - 実測されたバルク全エネルギー $E_{\text{bulk}}$ および 1 原子あたりのエネルギー（$-443.49\text{ eV/atom}$ 基準）の整合性を検証する。
  - 確定した $E_{\text{bulk}}$ を `fracture_metadata.json` に明記してからスラブ計算を開始すること。
- **総合データベースへの随時記録（必須）**:
  新しい条件（周期数、真空層、方位等）で計算が完了したら、必ず [`calc_surface_energy.py`](modular_aimd_framework/parameters_variable/calc_surface_energy.py) を実行して [`SURFACE_ENERGY_RESULTS.md`](SURFACE_ENERGY_RESULTS.md) および [`surface_energy_results.csv`](surface_energy_results.csv) に解析条件（DFT・MD）とエネルギー差分・表面破壊エネルギーを自動追記し、Google Drive（`G:\マイドライブ\MD_backup\`）にも同期すること。

---

## 2. 元素対応と Winmostar 可視化整合性
- **元素番号の厳格一致**:
  ASE `write_lammps_data` に従い、必ず **Type 1 = C (12.011)**、**Type 2 = Si (28.085)** を全スクリプトで統一すること。
- **XYZ 変換・可視化ルール**:
  `make_xyz.py` で LAMMPS dump を Winmostar 用 XYZ に変換する際は、原子 ID (`aid`) でソートし、元素マッピングを適用すること。未ソート出力は原子入れ替わり表示の原因となるため禁止。
- **Winmostar 表示**:
  - `md_animation.xyz` をドラッグ＆ドロップまたは `[ファイル] -> [開く]` し、`[MD] -> [アニメーション表示]` で表面再構成アニメーションを確認可能。
  - `espresso.pwo` を直接開くことで SCF 収束曲線を確認可能。

---

## 3. Google Colab (T4 GPU) プロセス管理と MDI 安定実行
- **`killall python3` の絶対禁止**:
  Colab の Jupyter カーネル（`colab_kernel_launcher`）が終了して SSH/ngrok 切断を引き起こすため、`killall -9 python3` は禁止。プロセス停止は `killall -9 pw.x lmp` または `pkill -f qe_mdi_engine` を用いること。
- **ASE + MDI の DummyMPI 必須化**:
  `import mdi` 後に ASE を用いる際は、必ず `ase.parallel.world = ase.parallel.DummyMPI()` を設定して `MPI_Comm_size` 早期呼び出しによる SIGABRT クラッシュを防ぐこと。
- **自動バックアップ**:
  Colab 側 `/content/drive/MyDrive/MD_backup/` への 5 分間隔同期を維持すること。

---

## 4. 0 K 構造緩和と 300 K 有限温度 AIMD の厳格な役割分担
- **表面破壊エネルギー $\gamma$ の算出（0 K minimize）**:
  表面破壊エネルギー $\gamma = \frac{\Delta E}{2A}$ は $T = 0\text{ K}$ の基底状態エネルギー差として定義される。先行研究（Rauls et al. 1999）との比較検証は、必ず 0 K の共役勾配法（CG法 `minimize`）による表面構造緩和を用いて行い、熱振動やエントロピーを混入させないこと。
- **有限温度 AIMD（300 K NVT）の運用**:
  表面再構成構造の熱的安定性や将来のき裂進展を評価する際は、必ず **0 K 緩和済み構造（`slab_10-10_relaxed.data`）を初期構造とし、タイムステップ 1.0 fs、スラブ重心ドリフト防止（`fix momentum`）、標準 1.0 ps（1,000 steps）** で実施すること。

## 5. リアルタイム計算監視プロトコル
- 長時間の Colab 第一原理計算実行時は、本アプリ上で常時進捗を可視化するため、ターミナル用カラーモニター（`python3 stream_iteration.py`）およびエディタ用リアルタイム同期（`live_espresso.pwo`）を提供・維持すること。

---

## 6. 真空層厚さ依存性とスラブCG緩和の早期完了判定プロトコル
- **臨界遮断距離の確定**:
  真空層 10 Å と 5 Å では表面破壊エネルギーが完全一致（$\Delta \gamma = 0.0003\text{ J/m}^2$）し、相互作用は完全に遮断される。一方、2.5 Å では相互作用によりスラブ全エネルギーが $+0.38\text{ eV}$ 上昇（$\gamma \approx 2.4703\text{ J/m}^2$）。臨界真空厚さは **$2.5\text{ \AA} \sim 5.0\text{ \AA}$** である。
- **DFTノイズフロアと早期完了判定（重要）**:
  QEのSCF収束閾値（`1.0e-5 Ry`）に伴い、原子力の数値ノイズ限界は $\approx 0.0002\text{ Ry/au}$（$\approx 0.006\text{ eV/\AA}$）となるため、LAMMPSの `ftol = 1.0e-3 eV/Å` を永遠に満たさない場合がある。
  **「全エネルギーが小数第4位まで固定」「変位量 $\Delta r_{\max} \le 10^{-6}\text{ \AA}$（完全静止）」「Total force が $\sim 0.0002\text{ Ry/au}$ で停滞」** の 3 条件を満たした場合は構造緩和 100% 完了と判定し、直ちに安全停止・成果物確定を行うこと。

---

## 7. 論文・報告書・ポスター向けグラフ体裁仕様の厳格順守と生データ忠実性
- **文献値の厳格同定**:
  - 2H-SiC $\{10\bar{1}0\}$ m 面の文献値は、Rauls et al. 1999 (Solid State Commun. 111, p.462 Fig.2) の実測値 **$3.03\text{ J/m}^2$** ($188\text{ meV/\AA}^2$) を唯一の基準線とする。
  - 水平破線: $3.03\text{ J/m}^2$ (`ls='--'`, `lw=1.2`, `#222222`)。
  - ラベル: **太字「文献値」** + **Times New Roman Bold「(3.03 J/m²)」**（12.5 pt）。
- **データの客観性・透明性・捏造・恣意改変の絶対禁止**:
  - プロットする表面破壊エネルギーは、各計算フォルダ直下の生ログ（`espresso.pwo`, `log.lammps`）から直接算出した実測値のみを用い、文献値に近づけるためのデータ加工や操作は一切行わないこと。
- **比較グラフ基本仕様（ユーザー承認済み体裁 [`GRAPH_STYLE_SPEC.md`](GRAPH_STYLE_SPEC.md)）**:
  - 形状: 長方形（5.6 × 4.4 インチ, 300 dpi）
  - プロット点: 中抜き紫三角マーカー（`marker='^'`, `facecolors='none'`, `#8A2BE2`, `s=70`, `linewidths=1.6`）、線で結ばない
- **真空層厚さ依存性グラフ仕様**:
  - 軸ラベル: 縦軸 `表面破壊エネルギー [$\mathrm{J/m^2}$]`, 横軸 `真空層の厚さ [$\mathrm{\AA}$]`（14.5 pt, 単位は Times New Roman）
  - 縦軸範囲 & 目盛り: **$2.4 \sim 3.2\text{ J/m}^2$**（0.1 刻み: `2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2`、Times New Roman 11.5 pt, 内向き）
  - 横軸範囲 & 目盛り: $0.0 \sim 16.0\text{ \AA}$（2.0 刻み: `0.0, 2.0, 4.0, ... 16.0`）
- **周期数依存性グラフ仕様**:
  - 軸ラベル: 縦軸 `表面破壊エネルギー [$\mathrm{J/m^2}$]`, 横軸 `周期数 [periods]`（14.5 pt, 単位は Times New Roman）
  - 縦軸範囲 & 目盛り: **$2.2 \sim 3.2\text{ J/m}^2$**（0.1 刻み: `2.2, 2.3, ... 3.2`）
  - 横軸範囲 & 目盛り: $1 \sim 7$（目盛り: `2, 4, 6`）
  - 保存名: 内容が一目でわかる具体的名称（例: `周期数と表面破壊エネルギーの関係.png / .pdf / .svg`）

## 8. 指示書テキストファイル経由の 3 種推移グラフ自動生成・保存定例化システム（必須・恒久ルール）
- **指示書テキストファイル (`RELAXATION_GRAPH_PROTOCOL.json`) の必須配備**:
  ワークスペースルートおよび各計算ディレクトリに、3 種推移グラフの体裁（Word 8.0cm × 6.2cm, 600dpi, PNG/PDF/SVG, MS明朝 10.5pt, Times New Roman 9.5pt, 中抜き紫三角 `#8A2BE2`）を定義した指示書テキストファイルを常備すること。
- **汎用自動生成エンジン (`auto_generate_progression_graphs.py`) の連動**:
  計算実行スクリプト（`run_colab_gpu.sh`）の終了部（`wait $LMP_PID` 直後）には、必ず以下を組み込むこと：
  ```bash
  python3 auto_generate_progression_graphs.py
  ```
- **自動保存先解決ルール**:
  `auto_generate_progression_graphs.py` は、同ディレクトリの `master_run_gpu.sh` 内の `BACKUP_DIR`（Google Drive パス）を自動検出し、ローカル計算ディレクトリと Google Drive バックアップフォルダの両方へ即座に 3 種グラフ（①全エネルギー推移、③全原子作用力推移、④SCF補正値推移）を自動ダイレクト保存すること。手動操作や後付け生成に依存してはならない。
- **ログとグラフの 1 対 1 対応・他フォルダ流用禁止の保証**:
  各計算ディレクトリおよび Google Drive バックアップフォルダに保存される 3 種推移グラフは、必ず**そのフォルダ直下の `espresso.pwo` および `log.lammps` から直接パースして生成された固有のデータであること**を保証する。他フォルダのグラフファイルをコピー・流用することは厳禁とする。
- **体裁仕様（厳格準拠）**:
  - 寸法: 横 8.0 cm × 縦 6.2 cm（Word 配置最適化）
  - フォント: 軸ラベル MS明朝 10.5 pt、目盛り数字 Times New Roman 9.5 pt、数式 STIX
  - マーカー: 中抜き紫三角マーカー（`marker='^'`, `facecolors='none'`, `edgecolors='#8A2BE2'`, `s=45`, `linewidths=1.2`）＋折れ線（`#8A2BE2`, `lw=1.2`）
  - 枠線・目盛り: 4辺枠線（`top=True, right=True`）、内向き目盛り（`direction='in'`）
  - 文献値の点線は不要。

## 9. スラブ構造緩和における最適化収束条件標準 (`minimize 1.0e-6 1.0e-2 100 150`) と非上書き原則（必須）
- **最適化収束条件の恒久標準（全規模スラブ共通）**:
  QEのSCF収束閾値（`conv_thr = 1.0e-5 Ry`）に伴う Hellmann-Feynman 力のノイズ限界（$\approx 0.005 \sim 0.008\text{ eV/\AA}$）を考慮し、2周期・4周期・6周期を含むすべてのスラブ構造緩和入力スクリプトで以下を標準とする：
  ```lammps
  minimize 1.0e-6 1.0e-2 100 150
  ```
  - `ftol = 1.0e-2 eV/Å`（$= 0.010\text{ eV/\AA} \approx 0.0004\text{ Ry/au}$）: 物理的な構造緩和完了時点で自然に自動正常終了させる。
  - `etol = 1.0e-6`: エネルギー底打ち（$\Delta E \le 0.06\text{ eV}$）による二重セーフティネット。
  - `maxiter = 100, maxeval = 150`: 安全上限ステップ数。
  - **実証済み妥当性**: 2周期・真空2.5 Å において、旧条件での未収束状態から本設定により 31分43秒 で自然収束し、表面破壊エネルギーの差異はわずか $+0.0006\text{ J/m}^2$（誤差 0.02%）と完全一致することが実証済み。
- **条件変更時の非上書き原則と新規ディレクトリ・ファイル作成**:
  収束条件やモデル条件（周期数・真空厚）を変更する際は、**既存のファイルを上書きせず、必ず新しく独立したディレクトリ（例: `calc_2H-SiC_10-10_<N>periods_vac<X>A/`）およびファイル（`in.lammps.optimized_conv` など）を作成して保存・実行すること**。
  Google Drive 上にも独立したフォルダ（例: `[101_0]<N>周期<X>Å/`）を必ず新規作成し、5分間隔の自動バックアップループを確立すること。

## 10. 結晶面切断（へき開面）の物理的前提厳守とモデル整合性（絶対遵守）
- **自然へき開面の物理的前提**:
  き裂進展・脆性破壊シミュレーションにおけるスラブ切断面は、エネルギー最小となる「粗結合面（$dz \approx 1.776\text{ \AA}$ の弱結合面）」でなければならず、強結合ペア（$dz \approx 0.888\text{ \AA}$）を引きちぎる切断は厳禁。
- **モデル拡張時の ASE surface 統一**:
  周期数変更（2周期 $\to$ 4周期 $\to$ 6周期）時は手動計算スクリプトを使わず、ASE `surface(bulk, indices=(1, 0, 0), layers=2*N)` で統一生成し、両端が密結合保持（外側が粗結合切断）であることを確認すること。
- **異常値の早期検知と妥当性評価**:
  表面破壊エネルギー $\gamma$ が文献値（$\approx 2.45\text{ J/m}^2$）から大きく乖離した場合、「スラブ厚み依存性」や「オーダーが合っている」などと安易に正当化せず、切断面の終端原子・結合状態を最優先で疑い検証すること。

詳細規約は [`.agents/rules/colab_t4_gpu_aimd_workflow.md`](.agents/rules/colab_t4_gpu_aimd_workflow.md) および [`.agents/rules/surface_fracture_slab_rules.md`](.agents/rules/surface_fracture_slab_rules.md) を参照すること。




