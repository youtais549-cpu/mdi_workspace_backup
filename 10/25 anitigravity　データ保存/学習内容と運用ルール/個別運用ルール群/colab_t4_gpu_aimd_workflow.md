# Google Colab (T4 GPU) 遠隔第一原理MD & 表面破壊エネルギー計算規約

Google Colaboratory (T4 GPU) 上で MDI (LAMMPS + Quantum ESPRESSO) 連成計算および表面破壊エネルギー評価を行う際は、本規約に厳格に従うこと。

---

## 1. Google Drive 自動同期・バックアップ規約
* **パスの対応関係**:
  * Windows 側: `G:\マイドライブ\MD_backup\`
  * Colab 側: `/content/drive/MyDrive/MD_backup/`
  * 両者は完全同期ディレクトリであるため、計算プロセス中の自動バックアップ先は必ず `/content/drive/MyDrive/MD_backup/` を指定すること。
* **バックアップループ**:
  * `master_run_gpu.sh` 内で 5分間隔のバックグラウンドループ（`while true; do ... sleep 300; done &`）を実行し、以下の拡張子を同期すること：
    `*.lammpstrj`, `*.xyz`, `*.log`, `*.pwo`, `*.pwi`, `nohup.out`
* **結果ファイルの上書き防止と個別アーカイブ規約（厳格義務）**:
  * 既存の計算結果（`dump.lammpstrj`, `espresso.pwo`, `md_animation.xyz`, `log.lammps`, `qe_engine.log` 等）を、後続の別計算（バルク計算、他の方位、異なるカットオフ等）によって直接上書きしたり、スクリプトの `rm -rf` で安易に一括消去することは**絶対禁止**。
  * 各計算が完了した際、または次の新しい計算を同一環境で開始する前には、必ずモデル名・面方位・計算種別・日付を付与した独立ディレクトリ（例: `2H-SiC_10-10_slab_relaxed_YYYYMMDD/`）を Google Drive およびローカルに作成し、全成果物を完全退避・保護すること。
  * 今回の成果物は `2H-SiC_10-10_slab_relaxed_20261020/`（Google Drive: `G:\マイドライブ\MD_backup\2H-SiC_10-10_slab_relaxed_20261020\`、ローカル: `results_2H-SiC_10-10_slab_relaxed_20261020/`）に永続保存されている。

---

## 2. Tesla T4 GPU (OpenACC / CUDA CC 75) 実行基準
* **VRAM とシステムサイズ制約**:
  * 360原子モデルは Colab のメインメモリ（RAM > 13.15 GB）不足により OOM クラッシュするため禁止。
  * 72原子モデル（$3\times 3\times 2$, カットオフ 40 Ry / 320 Ry）を採用すること（Tesla T4 15GB VRAM のうち実測約 9.4 GB を消費、GPU使用率 95%、43〜49W P0状態で高速・安定動作。所要時間は Step 0 初期収束約 7.5分、以降約 5〜7分/ステップ）。
* **対角化並列化設定**:
  * 単一 T4 GPU での実行時は、必ず `pw.x -ndiag 1` を指定すること（マルチGPU用スケーリングオーバーヘッドを回避）。
* **ライブラリ自動パス解決**:
  * `LD_LIBRARY_PATH` には、最新 NVHPC（`/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/` の `compilers/lib`, `math_libs/lib64`, `cuda/lib64`, `comm_libs/mpi/lib`）および `/usr/lib64-nvidia` を含めること。
* **MPI競合防止**:
  * Python の MDI エンジン側で子プロセス (`pw.x`) を起動する前に、環境変数 `OMPI_*`, `PMIX_*`, `ORTE_*` をクリアすること。

---

## 3. SSH 接続およびセキュリティ規約
* **公開鍵認証と権限 (600)**:
  * 秘密鍵 (`~/.ssh/id_ed25519`) のパーミッションは必ず `600`、ディレクトリは `700` を維持すること（644 だと SSH が秘密鍵を無視し `Permission denied (publickey)` になる）。
  * Colab 側の `/root/.ssh/authorized_keys` にローカルの公開鍵が登録されていることを前提とする。
* **動的ポート更新**:
  * ngrok のホスト/ポートが変更された場合は、`python3 workflow_cli.py config <host> <port>` を用いてワンコマンドで `.ssh/config` を更新すること。

---

## 4. ASE 元素ソートと LAMMPS / MDI 整合性ルール
* **元素ソートの法則**:
  * ASE の `write_lammps_data` は元素名をアルファベット昇順（C=1, Si=2）で書き出す。
* **LAMMPS 入力 (`in.lammps`)**:
  * `mass 1 12.011` (C)
  * `mass 2 28.085` (Si)
  * `fix 1 all mdi/qm elements C Si`
* **MDI エンジン (`qe_mdi_engine_core.py`)**:
  * `type_to_symbol = {1: 'C', 2: 'Si'}`
  ※これを誤ると Si と C のポテンシャルと質量が逆転し、計算結果が完全に破綻するため厳禁。

---

## 5. モジュール型フレームワーク (`modular_aimd_framework`) の運用規約
パラメータスタディを行う際は、コードの改変リスクを防ぐため、ディレクトリ分離ルールを厳守すること：
* **`parameters_variable/` (ユーザー編集対象)**:
  * `model_settings.py` (真空層厚さ `VACUUM_THICKNESS`、周期数 `N_PERIODS`、結晶面 `CLEAVAGE_PLANE`)
  * `dft_settings.py` (`ecutwfc`, `ecutrho`, `conv_thr`, `kpts`)
  * `in.lammps.template` (`minimize` vs `run`)
  * モデル変更時は `python3 generate_models.py` を実行してスラブ・バルク・`fracture_metadata.json` を一括更新。
  * 評価時は `python3 calc_surface_energy.py <E_slab> <E_bulk>` を実行。
* **`core_unchanging/` (ユーザー編集不要)**:
  * `qe_mdi_engine_core.py`, `master_run_gpu.sh`, `run_colab_gpu.sh`, `workflow_cli.py` は原則として直接編集しない。

---

## 6. Colab プロセス管理と QE GPU 実行規約
* **`killall python3` の絶対禁止**:
  * Colab 上で `killall -9 python3` を実行すると、Jupyter サーバー（`colab_kernel_launcher`）が強制終了し、ランタイム切断および ngrok トンネル切断が発生する。
  * プロセスを停止する際は必ず `killall -9 pw.x lmp` または `pkill -f qe_mdi_engine` を指定すること。
* **NVHPC HPC-X OpenMPI ラッパー規約**:
  * NVHPC でビルドされた `pw.x` は MPI プログラムであるため、実行時は `mpirun --allow-run-as-root -np 1` を通して起動する必要がある。
  * ラッパースクリプト `/content/bin/pw.x` は 1行目先頭バイトに必ず `#!/bin/bash` を記述すること（欠落すると `OSError: [Errno 8] Exec format error` となる）。
  * OpenMPI のセッションディレクトリ競合を防ぐため、`TMPDIR` および `--mca orte_tmpdir_base` を隔離すること。
  * ビルド済みバイナリは Google Drive（`/content/drive/MyDrive/mdi_binaries/`）に自動退避させ、再起動時の即時再利用を行うこと。
* **MDI + ASE 連携時の DummyMPI 強制適用 (最重要)**:
  * `import mdi` を行うと内部的に `mpi4py` がインポートされる。ASE の `parallel.py` は `sys.modules` 内の `mpi4py` を検出すると自動的に MPI 並列モードを有効化し、`world.size` (`MPI_Comm_size`) を呼び出そうとして `The MPI_Comm_size() function was called before MPI_INIT was invoked` により Python プロセスごと SIGABRT クラッシュする。
  * 対策として、MDI Python エンジンでは ASE インポート直後に必ず以下を宣言してダミーコミュニケータを強制すること：
    ```python
    import ase.parallel
    ase.parallel.world = ase.parallel.DummyMPI()
    ```
* **MDI コマンド登録ノード規約**:
  * MDI 1.4+ ではコマンド登録前に `mdi.MDI_Register_Node("@DEFAULT")` を呼び出す必要がある。呼び出さないと `MDI_Register_Command` がエラーとなる。
* **Colab 切断防止 (Keep-Alive)**:
  * ブラウザの開発者ツール (F12) のコンソールで以下を実行することで、アイドル切断（15〜30分無操作）を防止できる：
    ```javascript
    function ClickConnect(){
      console.log("Colab Keep-Alive ping");
      document.querySelector("colab-connect-button").shadowRoot.getElementById("connect").click();
    }
    setInterval(ClickConnect, 60000);
    ```

---

## 7. 計算結果の可視化規約 (Winmostar 連携)
* **XYZ変換時の元素マッピングとIDソート**:
  * LAMMPS dump から XYZ への変換（`make_xyz.py`）では、必ず `type_to_elem = {1: 'C', 2: 'Si'}` を厳守すること。
  * 原子の並び順を原子ID（`aid`）でソートして書き出すこと（未ソートだとアニメーション再生時に原子が入れ替わる不具合が生じる）。
* **Winmostar での可視化手順**:
  * Windows 側の同期パス `G:\マイドライブ\MD_backup\<archive_name>\md_animation.xyz` を Winmostar にドラッグ＆ドロップまたは `[ファイル] -> [開く]` で開く。
  * `[MD] -> [アニメーション表示]`（または再生ボタン `▶`）により、表面原子の再構成・緩和プロセスを動画で確認する。最終フレームが完全緩和構造。
  * `espresso.pwo` を Winmostar で直接開くことで、SCFエネルギー収束曲線を可視化できる。
* **Windows コマンドラインからの直接起動例**:
  ```powershell
  & "C:\winmostar\winmostar.exe" "G:\マイドライブ\MD_backup\<archive_name>\md_animation.xyz"
  ```

---

## 8. リアルタイム計算監視プロトコル (Real-Time Monitoring)
Colab 上での長時間の QE / LAMMPS 計算進行中、Antigravity IDE 上からリアルタイムに進捗を把握できるよう、以下のツールを標準維持すること：
1. **ターミナル専用カラーモニター (`stream_iteration.py`)**:
   - `python3 stream_iteration.py` を実行することで、SSH 経由でリモートの `espresso.pwo` をストリーミング受信し、Iteration番号、Total Energy (Ry / eV)、Accuracy、経過時間を ANSI カラー付きでリアルタイム表示する。生ログ表示は `--raw`。
2. **エディタ画面へのリアルタイム同期 (`live_espresso.pwo`)**:
   - バックグラウンドでリモートログをローカルの `live_espresso.pwo` へ `tail -f` 転送し、ユーザーが IDE エディタでファイルを開いているだけで末尾にリアルタイム追記される環境を提供する。
3. **ワンショット進捗診断 (`check_progress.py`)**:
   - リモートのプロセス稼働状況、GPUメモリ/使用率、最新の SCF 収束ステップをスナップショット判定するツールを常備する。

---

## 9. 指示書テキストファイル経由の 3 種推移グラフ自動生成・保存定例化システム
* **標準指示書 (`RELAXATION_GRAPH_PROTOCOL.json`) の必須配備**:
  ワークスペースルートおよび各計算ディレクトリに、3 種推移グラフの体裁（Word 最適化 8.0cm × 6.2cm, 600dpi, PNG/PDF/SVG, MS明朝 10.5pt, Times New Roman 9.5pt, 中抜き紫三角 `#8A2BE2`）を定義した指示書テキストファイルを常備すること。
* **汎用自動生成エンジン (`auto_generate_progression_graphs.py`)**:
  計算実行スクリプト（`run_colab_gpu.sh`）の終了部（`wait $LMP_PID` 直後）には、必ず以下を組み込むこと：
  ```bash
  python3 auto_generate_progression_graphs.py
  ```
* **自動保存先解決ルール**:
  `auto_generate_progression_graphs.py` は、同ディレクトリの `master_run_gpu.sh` 内の `BACKUP_DIR`（Google Drive パス）を自動検出し、ローカル計算ディレクトリと Google Drive バックアップフォルダの両方へ即座に 3 種グラフ（①全エネルギー推移、③全原子作用力推移、④SCF補正値推移）を自動ダイレクト保存すること。手動操作や後付け生成に依存してはならない。


