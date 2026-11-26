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
