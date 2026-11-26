---
name: lammps_qe_mdi_winmostar
description: Best practices and workflows for LAMMPS + Quantum ESPRESSO on-the-fly MDI coupled molecular dynamics simulation in Linux/WSL, automatic new project template setup via init_project.sh, and trajectory visualization in Winmostar on Windows via wm command.
---

# LAMMPS + Quantum ESPRESSO MDI Coupling & Winmostar Visualization Master Skill

このスキルは、LAMMPS を古典・第一原理結合分子動力学 (MD) のドライバーとして使い、Quantum ESPRESSO (`pw.x`) を力とエネルギーの算出エンジンとして連携（オンザフライQM/MM・マルチ・タイムゾーン計算等）を実行し、その結果を Winmostar 等で分析・可視化する際に自動適用すること。

## 1. コアシステム構成 (TCP Server & Client Model)
- **直接の `pw.x -mdi` は使用禁止**: MDI未統合ビルドの `pw.x` はポートコマンド引数をスキップするため、ドライバー側 (LAMMPS) が接続待ちでソケットハングアップする直接の原因となる。
- **必ず ASE ＋ pymdi による Python 中継エンジン (`qe_mdi_engine.py`) をブリッジサーバーとして介在させる**:
  - **LAMMPS 側 (ドライバー / サーバー待機)**:
    `lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021" -in in.lammps &` (※ `-hostname localhost` を付与しない！)
  - **Python 中継側 (エンジン / クライアント接続)**:
    `python3 qe_mdi_engine.py -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost"`

## 2. 新規プロジェクト（新しい計算フォルダ）の自動構築作法
- 新しく計算を行う際（温度違いや実験等）に手動でフォルダやスクリプトを作成せず、必ずルート直下にある **構築ユーティリティ `init_project.sh`** を実行してフォルダを生成させる。
  ```bash
  cd ~/mdi_workspace
  ./init_project.sh <新フォルダ名>
  ```
- これにより、実行スクリプト `run.sh`・`qe_mdi_engine.py`・`make_xyz.py`・各種擬似ポテンシャル (`.upf`)・入力ファイル (`in.lammps`) が一斉クローン化され、移動後 `./run.sh` 打鍵で計算が開始できる。

## 3. Quantum ESPRESSO 側の SCF 収束・振動制御パラメータ
- オープンシェル状態やステップ進行によるエネルギー振動（反復100回停止で結果未出力になる不具合）を防ぐため、ASE リレーエンジン内の `input_data` 設定において以下の項目を必須とする：
  ```python
  'system': {
      'ecutwfc': 40.0,
      'occupations': 'smearing',
      'smearing': 'gaussian',
      'degauss': 0.01
  },
  'electrons': {
      'conv_thr': 1.0e-5,
      'mixing_beta': 0.3,
      'mixing_ndim': 10,
      'electron_maxstep': 200
  },
  'control': {
      'tprnfor': True,
      'tstress': True,
      'disk_io': 'minimal'
  }
  ```
- ファイル衝突防止のため Espresso 計算機宣言時に `label='qe_mdi'` とし、起動コマンドを `-in qe_mdi.pwi > qe_mdi.pwo` に一致させる。
- LAMMPS の設定ファイル (`in.lammps`) で MDI 宛ての元素アサイン `fix 1 all mdi/qm elements Si C` を欠かさず明記すること。

## 4. Winmostar による最強・最速可視化の定石 (WSL から Windows オート呼び出し)
- 計算終了後にユーザーへご案内あるいはコマンド実行する際、生の `dump.lammpstrj` を直で開くと化学元素名不備による Winmostar の型不明エラーが起きることがあるため、**必ず `make_xyz.py` による標準 `.xyz` トラジェクトリ変換を済ます**こと。
  ```bash
  python3 make_xyz.py        # => Si や C など元素情報がついた md_animation.xyz を高速出力
  wm md_animation.xyz        # => Winmostar がポップアップし 3D 構造をただちに描画！
  ```
- (`wm` エイリアスは `~/.bashrc` 内にある `/mnt/c/winmos11/winmostar.exe "$(wslpath -w "$1")" &` で構成されている。)

## 5. WSL/ローカル環境構築とビルド時のベストプラクティス
システム環境（sudo）を汚さずにローカル環境（WSL等）をセットアップする場合の知見：
- **Miniconda の利用**: ユーザー領域 (`~/miniconda3`) に Miniconda をインストールして依存関係を管理する。
- **Quantum ESPRESSO の Conda インストール**: conda-forge チャンネルではパッケージ名は `quantum-espresso` ではなく `qe` を指定する。(`conda install -c conda-forge qe ase cmake c-compiler cxx-compiler`)
- **Python モジュールの注意点**: `pip install pymdi` でインストールするが、Python スクリプト内でのインポート名は `import mdi` である。
- **LAMMPS + MDI ビルド時の CMake エラー回避**: MDI 連携を有効にして LAMMPS をソースから CMake でビルドする際、Python の開発用ヘッダー (`pyconfig.h` 等) が見つからずエラーになる場合は、`lammps/cmake/Modules/Packages/MDI.cmake` 内の `set(MDI_USE_PYTHON_PLUGINS ON)` になる箇所をコメントアウトし、強制的に `set(MDI_USE_PYTHON_PLUGINS OFF)` に変更してからビルドする。これにより不要な Python プラグイン依存をスキップし、ビルドを成功させることができる。

## 6. 計算の実行と長期間監視のベストプラクティス (AI 委譲)
- 計算（`./run.sh` 等）は長時間に及ぶため、ユーザーの画面切断などで中断されないよう、**基本的に AI（Antigravity）への `/goal` コマンドによる委任を前提とする**。
- ユーザーが計算実行を求めた場合、または `/goal` で指示された場合、AI はバックグラウンドで `run.sh` を実行し、完了まで監視を行う。
- 計算が完了した際は、AI が自動で `make_xyz.py` を実行してトラジェクトリ変換を済ませた上で、ユーザーに完了報告と Winmostar での可視化を促す。

## 7. Google Colab Pro (GPU) での大規模計算・移行のベストプラクティス
- **GPUアーキテクチャ不一致の罠 (Error 300)**: T4 GPUでコンパイルした `pw.x` は、A100 GPUなどの別世代のGPUで実行すると起動直後に `device kernel image is invalid (Error 300)` で即死する（Exit 127等になる）。GPU環境（Colab ProのA100等）をアップグレードした場合は、必ずそのGPUアーキテクチャ（A100なら `-DNVFORTRAN_CUDA_CC=80`）向けに**再コンパイル**すること。
- **NVHPC 24.7以降とQE 7.2の非互換性**: Quantum ESPRESSO 7.2 のGPU機能は CUDA Fortran (`cudafor`) に強く依存しているが、NVIDIAは NVHPC 24.1 以降でこれを廃止した。そのため、Colab上で最新版(24.7等)を入れるとコンパイルが100%失敗する。**必ず `nvhpc-23-11` (安定版) を指定してインストール**すること。
- **CMakeによる確実なビルド**: QEの古い `configure` スクリプトはCUDAの判定バグで自爆しやすいため、NVHPC環境でのコンパイルは必ず CMake を用いる。
  ```bash
  cmake .. -DCMAKE_C_COMPILER=nvc -DCMAKE_Fortran_COMPILER=nvfortran -DQE_ENABLE_OPENACC=ON -DQE_ENABLE_CUDA=ON -DNVFORTRAN_CUDA_CC=80 -DQE_FFTW_VENDOR=Internal
  make pw -j4
  ```
- **mpirun の闇とシングルトン起動の罠 (完全なるラッパーの作成)**: Colab (NVHPC) 環境で `pw.x` を `mpirun` なしで単独起動（シングルトン起動）させると、A100環境のMPIシステムでは通信待ちによる無限のデッドロック（フリーズ）に陥る。一方で、普通に `mpirun` で起動すると Colabの仕様により親の `LD_LIBRARY_PATH` が剥奪されライブラリ不足 (Exit 127) になる。
  **【最強の解決策】**: 127エラーとデッドロックを両方回避するため、環境変数を強制的に引き継ぐ `-x` オプションを付けた `mpirun` の起動ラッパースクリプトを作成し、ASE（中継エンジン）にはこれを叩かせること。
  ```bash
  cat << 'EOF' > /content/bin/pw.x
  #!/bin/bash
  export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/23.11
  export PATH=$NVHPC_HOME/compilers/bin:$NVHPC_HOME/comm_libs/mpi/bin:$NVHPC_HOME/cuda/bin:$PATH
  export LD_LIBRARY_PATH=$NVHPC_HOME/compilers/lib:$NVHPC_HOME/comm_libs/mpi/lib:$NVHPC_HOME/math_libs/lib64:$NVHPC_HOME/cuda/lib64:/usr/local/cuda/lib64:/usr/lib64-nvidia:$LD_LIBRARY_PATH
  $NVHPC_HOME/comm_libs/mpi/bin/mpirun --allow-run-as-root -x LD_LIBRARY_PATH -x PATH -np 1 /content/bin/pw.x.real "$@"
  EOF
  chmod +x /content/bin/pw.x
  ```

## 8. Colabの長期間実行と切断回避のベストプラクティス
- **90分無操作タイムアウトの回避**: PCがスリープしていなくても、Colabの画面上で90分間操作がないと強制切断される。これを防ぐため、計算開始後は必ずブラウザの開発者ツール（F12）のConsoleタブに以下のJavaScriptコードを貼り付けて実行し、裏で自動クリックさせること（PC自体のスリープ設定もオフにする）。
  ```javascript
  function ClickConnect(){
      console.log("切断防止コードを実行中...");
      document.querySelector("colab-connect-button").click();
  }
  setInterval(ClickConnect, 60000);
  ```
- **GPU自動接続の罠（完全自動化の禁止）**: Python（Selenium等）を用いて「翌朝に自動でColabを開き、GPU接続ボタンを押す」行為は、GoogleのreCAPTCHAに弾かれるだけでなく、Colabの利用規約（ボット禁止）に抵触しアカウントBANのリスクがある。そのため、長期間の計算を安全に行うには「LAMMPSのrestart機能によるGoogle Driveへのこまめな自動セーブ（append出力）」を設定しておき、**「翌日、手動で1回だけ接続ボタンを押し、前回からの再開セルを実行する」**という半自動運用が最も安全かつ最適なベストプラクティスとなる。
- **Colabローカルディスク消滅問題への対策**: 計算場所が `/content/...` の場合、インスタンス強制終了時（上限到達時など）に全データが消滅する。計算を中断せずに安全を確保するためには、別のセルで以下のような**「無限ループによる10分間隔でのGoogle Driveへのバックアップスクリプト」**を裏で回し続けること。
  ```bash
  while true; do
    cp /content/SiC_3x3x10_MD/restart*.rst /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null
    cp /content/SiC_3x3x10_MD/*.lammpstrj /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null
    cp /content/SiC_3x3x10_MD/espresso.pwo /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null
    sleep 600
  done
  ```

## 9. 【重要】2026年以降のColab仕様変更とASEアップデートに伴う致命的バグの回避策
- **Ubuntu 24.04 強制アップデートに伴う NVHPC 23.11 インストール不可問題**: Colabの裏側OSがUbuntu 24.04に更新されたことにより、NVHPC 23.11が依存する古いライブラリ (`libtinfo5`, `libncursesw5`) が消滅しインストールに失敗する。解決策として、Ubuntu 22.04の公式アーカイブから`.deb`を直接ダウンロードして強制インストールすること。
  ```bash
  wget -q http://archive.ubuntu.com/ubuntu/pool/universe/n/ncurses/libtinfo5_6.3-2_amd64.deb
  wget -q http://archive.ubuntu.com/ubuntu/pool/universe/n/ncurses/libncursesw5_6.3-2_amd64.deb
  dpkg -i libtinfo5_6.3-2_amd64.deb libncursesw5_6.3-2_amd64.deb
  curl -s -L https://developer.download.nvidia.com/hpc-sdk/ubuntu/DEB-GPG-KEY-NVIDIA-HPC-SDK | gpg --dearmor -o /usr/share/keyrings/nvidia-hpc-sdk-archive-keyring.gpg
  echo 'deb [signed-by=/usr/share/keyrings/nvidia-hpc-sdk-archive-keyring.gpg] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /' > /etc/apt/sources.list.d/nvhpc.list
  apt-get update
  apt-get install -y nvhpc-23-11
  ```
- **ASE 3.23.0+ の破壊的仕様変更 (`EspressoProfile` エラー)**: 最新のASEでは `Espresso` クラスから `command` 引数が廃止され、初期化方法が強制的に変更された。また `EspressoProfile` は `command` と `pseudo_dir` を位置引数として厳格に要求する。解決策として、**`profile = EspressoProfile(f"{pw_bin} -in PREFIX.pwi > PREFIX.pwo", "./")` のように引数名を付けずに渡し、それを `Espresso(profile=profile, ...)` に渡す確実な方式に書き換える**こと。

## 10. 実用的なDFT-MD本番計算における設定（リスタート機能とNVT）
- 実際のDFT-MDシミュレーション（例：300Kでの安定化など）では、計算時間の制約により途中でジョブが切れることが多いため、LAMMPS側でリスタート機能と適切な温度制御（NVTアンサンブル）を設定することが必須である。
- **リスタートファイルの保存**: `restart 10 restart1.rst restart2.rst` のように、一定ステップごとに2つのファイルを交互に上書き保存し、最新状態を保持する。
- **リスタートからの再開**: スクリプト冒頭の `read_data` 等の代わりに `read_restart restart1.rst` を読み込むことで、以前の速度・座標・系全体の情報を引き継いで再開できる。
- **NVTアンサンブルでの制御**: `velocity all create 300.0 12345` で初期温度を与え、`fix 2 all nvt temp 300.0 300.0 0.1` のようにして系全体を一定温度で制御する。
- **トラジェクトリの追記保存**: 中断からの再開時に以前の履歴を消さないよう、`dump_modify <ID> append yes` を設定して `.lammpstrj` ファイルに座標情報を追記していく構成にすること。

## 11. Colab環境特有の落とし穴とトラブルシューティングのベストプラクティス
- **フォルダの揮発性と復旧**: Colabの `/content` 配下はランタイム再起動（NVHPCインストール等）で完全に消滅する。エラー対応等で再起動が行われた場合は、必ず `colab_transfer.zip` 等を再アップロード・解凍し、計算用フォルダを確実に復旧させてから実行すること。
- **ブラウザ自動翻訳によるコード破壊（アンダーバー消失問題）**: ブラウザの翻訳機能（Google翻訳等）が有効な状態でColabのセルにスクリプトをペーストすると、`cd /content/SiC_3x3x10_MD` が `cd /content/SiC 3x3x10 MD` のように勝手にスペースに変換され、実行時に「No such file or directory」エラーを引き起こす。パスが見つからない場合は、Colabエディタ上のコードを目視で確認し、アンダーバーを手動で復元すること。
- **自動パッチ適用の無限ループと手動修正**: Pythonの文字列置換スクリプト（特に `try-except` の追加等、インデントに依存するもの）をパッチとして二重起動すると、コードがネストしてマトリョーシカ状に増殖し `IndentationError` となる。自動パッチは冪等（べきとう）性を担保するか、エラー時にはColabのエディタで直接開いて目視・手動で字下げを整えるのが最も安全かつ確実である。
- **Step 0 の沈黙 (LAMMPSの仕様上のフリーズ)**: 大規模系のMDI連携開始直後、最初のSCF計算（Step 0）が終わるまでLAMMPSは数十分〜数時間フリーズしたように見え、`log.lammps` や `dump_min.lammpstrj` には何も出力されない。これはエラーではなく正常な仕様（QEからの初期力とエネルギーの計算完了・返却待ち）であるため、焦らずに `espresso.pwo` の `iteration` を監視するよう案内すること。

## 12. 大規模システムでの構造最適化 (minimize) の罠と確実な収束判定設定
- **巨大な系でのエネルギー変化率（etol）による早上がりの罠**: LAMMPSの `minimize etol ftol iter eval` コマンドにおいて、第1引数の `etol`（エネルギー変化率の許容値）は、系全体の総エネルギーに対する相対変化を意味する。系が数百原子に及ぶと総エネルギーが巨大になるため（例：数万〜数十万 eV）、`etol=1.0e-4` (0.01%) でも実質的なエネルギー変化幅が数eV〜数十eVとなり、「十分な最適化が行われる前に終了条件を満たして早上がりしてしまう」という現象が多発する。
- **解決策**: 第一原理MDや大規模システムの構造最適化においては、**エネルギーの変化率条件は必ず `0.0` に設定し、純粋に「力の許容値（ftol）」のみで終了判定させるのが鉄則**である。
  ```lammps
  # 誤り (巨大系では即終了する)
  minimize 1.0e-4 1.0e-4 100 1000
  
  # 正しい (力の条件のみで確実な最適化を行う)
  minimize 0.0 1.0e-3 100 1000
  ```
- なお、DFT計算において `ftol=1.0e-6` は過酷すぎるため、`1.0e-3` または `1.0e-4` eV/Å 程度を設定するのが現実的である。

## 13. クラウド(Colab)からローカルNASへの完全自動バックアップ同期 (Google Drive リレー方式)
- **プライベートIPへの直接アクセスの壁**: Colabはクラウド環境のため、直接ローカルネットワーク内のNAS（例：192.168.12.69）にアクセスしてデータを保存することはできない。
- **解決策 (バケツリレー方式)**: 
  1. Colab側からは10分おきにGoogle Drive (`/content/drive/MyDrive/...`) にデータを退避させる（すでにバックアップループとして実装済み）。
  2. 手元のWindows PCの「Google ドライブ」アプリがこれを同期し、`G:` ドライブ等を更新する。
  3. ローカルのWSL (Linux) 環境から `G:` ドライブとNAS (`/mnt/nas` 等) を同時にマウントし、`rsync` による自動差分コピーを裏側でループ実行する。
- **実装例**: `setup_nas_sync.sh` のようなスクリプトで `mount -t cifs //192.168.12.69/...` を行い、`nohup` で `rsync` ループを回すことで、完全自動の2重バックアップ（Drive ＆ NAS）が実現可能。

## 14. 構造最適化(minimize)の途中再開 (dumpファイルからの座標復元)
- **minimize計算はrestartファイルを使えない**: LAMMPSの仕様上、構造最適化の途中経過は `restart` コマンドで安全に復元しにくい場合がある。確実なのはダンプされた最後の座標から上書き再開すること。
- **read_dump による復元**: `in.lammps` において、`read_data` で初期構造（トポロジーと質量）を読んだ直後に、**`read_dump dump_min.lammpstrj <再開したいステップ数> x y z box yes`** を追加するだけで、特定のステップの座標とセルサイズを完璧に復元できる。
- **追記設定の忘れに注意**: 再開後、以前のトラジェクトリを消去しないように `dump_modify 1 append yes` を設定しておくこと。

## 15. 【極めて重要】minimize + MDI 特有の挙動と監視トラップ
- **タイムステップ番号の初期化**: `read_dump` を使って途中から再開した場合でも、内部のタイムステップ（出力される `ITEM: TIMESTEP` の数字）は指定ステップ（例: 10）から継続せず、再び `0` または `1` から出力され始める。そのため、ダンプファイルの更新を監視する際は特定の数字（「10」等）を探すのではなく、**「ITEM: TIMESTEP の出現回数（ブロックの総数）が増えたか」**をカウントして判定する必要がある。
- **1ステップ内の複数回SCF計算（ラインサーチ）**: `minimize` コマンドはMD計算（`run`）と異なり、1ステップを進める間に「ラインサーチ」として複数回 MDI（QE）へ力の計算を要求する。そのたびに ASE の `EspressoProfile`（`>` で出力する仕様）によって **`espresso.pwo` ファイルは上書きされ、iteration が 1 に戻り小さくなる**。これはエラーによるリセットではなく、単なる「次の座標での力の評価開始」を意味する正常な挙動であるため、焦って停止させないこと。

## 16. 長時間計算における「進行と停止のハイブリッド監視」のベストプラクティス
- **Colab特有の「無言の死（サイレント・ハング）」**: Colab (Pro含む) の12時間制限やアイドル判定に引っかかった場合、エラーログを吐くことなくインスタンスが突然消滅する。この時、ローカルへのDrive同期も停止するため、「エラーは出ていないがファイルが一切更新されない」という現象が起きる。
- **ハイブリッド監視スクリプトの導入**: 長時間の計算を監視する際は、「`dump` ファイルのブロック数増加（進行）」だけでなく、**「`espresso.pwo` 等の出力ファイルの最終更新時刻 (`stat -c %Y`) を定期チェックし、30分以上更新が無ければ停止とみなす」**という両面待ち（ハイブリッド）の Bash スクリプトをバックグラウンドで起動することが最も確実なベストプラクティスである。
- **UI最小化とバックグラウンド監視の永続性**: AIが `run_command` で起動した監視プロセスはローカル（WSL等）のバックグラウンドプロセスとして独立して稼働するため、**ユーザーがブラウザのタブを最小化しても監視は完全に続行される**（PCやWSL自体を落とさない限り有効）。ユーザーにはこの点を伝えて安心してもらうこと。

## 17. 【超重要】Google Drive 等のバックアップ領域への安易な `cp *` の絶対禁止
- **事故のメカニズム**: 計算環境（Colab等）の揮発に備え、Google Driveへファイルをバックアップしている運用において、「ローカル（WSL等）に足りないファイルがあったから、ローカルのフォルダ内を `cp *` でまとめてGoogle Driveにコピーして補完しよう」と安易に考えると、**ローカル側に残っていた「0バイトのダミーファイル」や「古いバージョンのログ」で、Google Drive上の最新の貴重な計算結果（`dump_min.lammpstrj` や `espresso.pwo` 等）を上書きして完全に破壊してしまう**という大事故に直結する。
- **防止策**: 
  1. ファイルをバックアップ領域（Google Drive等）へ送信・補完する際は、横着して `cp *` を使わず、**必ず必要なファイル名だけを指名して個別コピー**すること。
  2. 万が一、誤ってGoogle Drive上の計算結果を上書きしてしまった場合は、Google Driveの標準機能である**「版の管理（バージョン履歴）」機能**をユーザーに案内することで、数十日以内のデータであれば以前のバージョンに即座に復旧させることが可能である。AI自身がミスをした場合は直ちにこのリカバリ手順を提示すること。

## 18. Colabでの大規模システム(300原子超)におけるMDIバグ回避と独自コンパイルの鉄則
- **`apt` 版 pw.x (v6.7) のバッファオーバーフロー**: Ubuntu (Colab標準) で `apt install quantum-espresso` で入る古い `pw.x` は、標準入力から数百原子の座標 (`ATOMIC_POSITIONS`) を一括で読み込もうとすると、内部のFortran/Cレベルでバッファオーバーフローを起こし `status 134` で即死する。大規模システムでMDIを実行する場合、絶対に `apt` 版を使用してはならない。
- **NVHPCコンパイル済みバイナリとMDI TCP競合による自爆**: NVHPCでビルドされた `pw.x` は内部で HCOLL (Hierarchical Collectives) 通信ライブラリを用いる。これをASE(MDI中継スクリプト)の `subprocess` 経由で実行すると、HCOLLがソケットを生成しようとして競合を起こし `hcoll_socket_channel` エラー (`MPI_ABORT 9035`) で強制終了する。ポート番号を変えても根本解決にはならない。
- **解決策 (システムMPIでのソースコンパイル)**: 大規模系のMDI結合計算をColabで安定稼働させるための唯一の正解は、**システム標準の `mpif90` (OpenMPI) と `libopenblas-dev`, `libfftw3-dev` を使って、Quantum ESPRESSO (v7.3等) を独自コンパイルすること**である。
  ```bash
  apt-get install -y libfftw3-dev libopenblas-dev
  ./configure BLAS_LIBS='-lopenblas' LAPACK_LIBS='-lopenblas' FFT_LIBS='-lfftw3'
  # Colab環境ではMKLが不完全に存在しconfigureが誤検知するため、make.inc の MANUAL_DFLAGS に手動で -D__FFTW3 を追記する
  sed -i 's/MANUAL_DFLAGS  =/MANUAL_DFLAGS  = -D__FFTW3/' make.inc
  make clean && make pw -j4
  ```
- **実行時の環境変数分離**: LAMMPSはNVHPCでビルドされているためNVHPCの `mpirun` と `LD_LIBRARY_PATH` が必要だが、システムMPIでビルドした `pw.x` にNVHPCの環境変数が混ざるとクラッシュする。そのため `run_colab.sh` では全体に `export` せず、**LAMMPS起動時のみインラインで環境変数を付与 (`env LD_LIBRARY_PATH=... mpirun ... lmp`)** し、Python/ASE 側（`pw.x` を呼ぶ側）には一切のNVHPC環境変数を継承させない分離構成にするのがベストプラクティスである。

## 19. ColabでのOOM(メモリ不足)クラッシュとGPUフォールバックのサイレント障害の特定
- **OOMによる無言のクラッシュ (Exit 1)**: Colabの無料枠 (使用可能メモリ約11.6GB) において、360原子規模の系 (`ecutwfc=40.0`) をCPUで計算させると、要求RAM (>13.15GB) が上限を超過する。この時 `pw.x` はエラーメッセージを出さず、`Starting wfcs are xxx randomized atomic wfcs` と出力した直後に `malloc` 失敗やOOM Killerにより **Exit code 1** でサイレントクラッシュする。
- **LAMMPS側の偽のエラーメッセージ (Red Herring)**: `pw.x` がクラッシュしてPython MDI中継エンジンが終了すると、LAMMPS側はソケットエラーで強制終了 (Abort) する。このAbort処理中、NVHPC OpenMPIは `The MPI_Comm_size() function was called before MPI_INIT was invoked` という一見するとMPIの初期化エラーのようなメッセージを吐くことがあるが、これは**単なる終了処理のバグによる偽陽性（Red Herring）**であり、真の原因は `pw.x` のクラッシュ側にある。
- **GPUフォールバックの確認**: NVHPCでGPU対応としてビルドした `pw.x` でも、GPUアーキテクチャの不一致やドライバの未認識などが発生した場合、**エラーを出さずに勝手にCPUモードにフォールバック**して計算を開始してしまう。実行時は必ず `espresso.pwo` の先頭を確認し、`GPU acceleration is ACTIVE` の表記があるか確認すること。`running on X processor cores` とだけ出ている場合はCPUで動作しており、前述のOOMクラッシュの直接の原因となる。
- **MDI実行時の環境変数の分離と注入**: 同一Colabノード内でLAMMPSと `pw.x` の2つの `mpirun` を並行動作させる際、グローバルな `OMPI_` 変数（`OMPI_ALLOW_RUN_AS_ROOT`など）が競合を引き起こす。中継用Pythonスクリプト内では `os.environ` から `OMPI_*` や `PMIX_*` を削除し、ASEの `EspressoProfile` の `command` 引数の中でインラインで `env OPAL_PREFIX=... mpirun ... pw.x` のように**明示的に環境変数とmpirunを注入する構成**が最も安全である。

## 20. Colabの通信安定化（Ngrokの必須化）とカーネル破壊の回避、およびNVHPCビルドの罠
- **Cloudflare トンネル (trycloudflare) の不安定さ**: 匿名で利用できる `cloudflared` トンネルは、無料枠の制限により、ファイルの転送 (`scp`) や一定の通信量を超過すると即座に `websocket: bad handshake` を吐いて強制切断される。長時間の計算監視やファイル転送を行う場合は、**必ず `ngrok tcp 2222` を使用してSSHトンネルを構築すること**。
- **Colabカーネルの自爆 (killall python3 の厳禁)**: 計算リセット用に `killall -9 pw.x lmp python3` のようなコマンドをColabへ送ると、Colabを動かしているシステムの大元である Jupyter Kernel (`ipykernel` = `python3`) ごと死滅してしまう。結果として「ランタイムがクラッシュしました」となり、バックグラウンドの `ngrok` や `sshd` も道連れに全滅する。プロセスをkillする際は、**絶対に `python3` を一括指定してはならない** (`qe_mdi_engine.py` のように完全一致で絞るか、`pw.x` や `lmp` のみに留めること)。
- **NVHPCによる GPU版 `pw.x` と HPC-X OpenMPI の致命的相性 (Error 9035)**: ColabのT4 GPU向けに NVHPC でビルドした `pw.x` を HPC-X (OpenMPI) 経由で実行すると、起動直後に `*** error in Message Passing (mp) module *** error code: 9035` となり、直後に `The MPI_Comm_size() function was called before MPI_INIT was invoked` を引き起こしてAbortする。これは NVHPC 付属の OpenMPI が Colabコンテナ環境と激しく競合するためであり、環境変数 (`OMPI_MCA_coll_hcoll_enable=0` 等) の小手先の調整では回避できない。GPU対応の `pw.x` をColabで動かす場合は、**システム提供のOpenMPI (`mpif90`) と NVIDIA HPC SDK (コンパイラのみ) を組み合わせて独自ビルド**するか、コンパイル不要なCPU版 (`apt install quantum-espresso`) にフォールバックする決断が必要である。

## 21. Colab (T4 GPU) における完全分離型のMDI実行アーキテクチャ (2026年最新)
- **環境変数の完全分離とシリアルGPUビルド**: Colab上の NVHPC OpenMPI と Ubuntu システム OpenMPI が競合して `opal_init` で死ぬ問題（Exit 127/Abort）を回避する決定版。LAMMPSとQEを同じ `mpirun` や共通のスクリプト環境変数で起動すると破綻する。解決策として、NVHPCで**MPIなし（シリアル）＋GPU有効**の `pw.x.serial` をコンパイルし、ASE(中継エンジン)からは純粋に `env LD_LIBRARY_PATH=... /content/bin/pw.x.serial` として直接呼び出す構成が最も安定する。
- **メモリ制約とGPU VRAM限界への対応 (OOMクラッシュ回避)**: ColabのT4 GPU (15GB VRAM) を用いる場合、360原子のSiCスーパーセルで `ecutwfc=40.0` のまま実行すると、`Estimated max dynamical RAM` が13GBを超過し、QE側が `cuMemAlloc returned error 2: Out of memory` でクラッシュする。
  - MDIの動作確認やテスト用途であれば、ASEエンジン側の設定を `ecutwfc=25.0` 程度まで下げることで要求メモリを約6.5GBまで圧縮でき、T4 GPUでも正常にMDサイクルを回すことが可能になる（物性値を出す本計算の際はスパコン等へ移行すること）。
- **ローカルNASへの rsync バックグラウンド同期**: Google Driveへのコピーだけでなく、手元（ローカルエージェント側）から `nohup bash -c 'while true; do rsync -avz colab:/content/... /mnt/nas_backup/... > /dev/null 2>&1; sleep 300; done' &` のようなデーモンプロセスを走らせることで、計算結果を確実にNASへ自動同期させる運用が最も安全で効果的なベストプラクティスである。
