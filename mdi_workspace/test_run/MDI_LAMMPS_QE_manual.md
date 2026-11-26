# LAMMPS と Quantum ESPRESSO を用いた MDI 結合分子動力学 (MD) 計算＆ Winmostar 連携公式マニュアル決定版

作成日時: 2026年7月25日
実行環境: Linux (WSL) / Windows (Winmostar V11) / Atomic Simulation Environment (ASE) / Python MDI

---

## 1. 概要とアーキテクチャ設計

LAMMPS（古典力学・ドライバ）と Quantum ESPRESSO / `pw.x`（電子状態計算・計算エンジン）を結合してオンザフライ分子動力学・第一原理計算を実施する際、標準ビルドされた `pw.x` が MDI (Model-Driven Interoperability) オプション (`-mdi`) を読み飛ばす問題があり、スタンドアローン起動によるソケットハングがおきる事象を完全に解決しました。

```
+-----------------------------------+             TCP Socket (localhost:8021)             +------------------------------------------------+
|       LAMMPS (MDI Driver)         | <=================================================> | Python 中継エンジン: qe_mdi_engine.py          |
| -role DRIVER                      |  Commands: >NATOMS, >CELL, >COORDS, >ELEMENTS...    | -role ENGINE                                   |
| -method TCP -port 8021            |                                                     | (ASE Atoms オブジェクト経由で pw.x を駆動)        |
+-----------------------------------+                                                     +------------------------------------------------+
```

---

## 2. 実務向け：新プロジェクト（新しいフォルダ）でのシミュレーション展開テクニック
新しくプロジェクトを作る際は、ワークスペース根底 (`~/mdi_workspace`) に用意した **自動構築スクリプト `init_project.sh`** で一発展開してください。

```bash
cd ~/mdi_workspace
./init_project.sh <新計算のフォルダ名>   # 例: ./init_project.sh run_SiC_500K
```

これにより、計算ループに必要な以下の完全セットが新フォルダに配備されます：
1. `run.sh` (起動統合スクリプト)
2. `qe_mdi_engine.py` (Python ASE+MDIラッパー)
3. `make_xyz.py` (Winmostar 向け原子トラジェクトリ自動変換用)
4. `in.lammps` + 各種ポテンシャル (`Si.upf`, `C.upf`)

新フォルダ内でそのまま `./run.sh` を打ち込めばただちに結合MDシミュレーションが完遂します！

---

## 3. 計算結果の Winmostar（Windows本体側）への最速・エラーゼロ可視化法
LAMMPS から吐き出される生の `dump.lammpstrj` には元素名（Si や C）が入っていないため、そのままWinmostarへ食べさせると自動判定エラーになる場合があります。

最速・高精度な解決作法として **「 `.xyz` トラジェクトリへ一度変換してから `wm` コマンドで開く」** 構成を利用してください。

### 【極上の 2行 連携オペレーション】
計算が終わったら、その場（ターミナルウインドウ）で以下を実行します：

```bash
python3 make_xyz.py        # 1秒で element(元素名) 付き動画データ md_animation.xyz が生成される！
wm md_animation.xyz        # Windows 上の Winmostar V11 が即自動起動し、3D美麗アニメを即再生可能！
```

### 💡 補足：どうして `wm` という短いコマンドで Windows ソフトに引き渡せるのか？
当環境の `~/.bashrc` の中に以下の特殊機能（関数 `wm`）をおまとめセットしたためです。
- Linux 側のローカルファイル名を `$(wslpath -w "$1")` によって Windows 側が読めるパス（`\\wsl.localhost\Ubuntu\...`）へ内部変換し、
- `C:\winmos11\winmostar.exe` （Windows本体インストール先）に向けて投げつけて開かせます！

---

## 4. トラブル対応集（Tips）

| 現象 | 理由 | 正しいアプローチ |
| :--- | :--- | :--- |
| **`wm` コマンドで Failed to determine file type が出る** | 生の `.lammpstrj` を直指定したため、元素記号 (Si/C) が不在で自動認識ミスを起こすため。 | 付属の `python3 make_xyz.py` を動かして作られる **`md_animation.xyz`** のほうを指定して呼び出す。 |
| **LAMMPSの途中で `Could not accept connection` と出る** | コマンド直打ち等で LAMMPS 側に `-hostname localhost` をつけたままにしてしまい、両者がクライアントになったため。 | 配備済みの **`./run.sh`** または新プロジェクト用 **`init_project.sh`** から作られた環境を使うことで未然にゼロ保証。 |
| **別の元素 (Fe, H 等) や別の組み合わせに変えたい** | 現時点では Si (1) と C (2) 構成になっているため。 | ①対応する `.upf` をフォルダに増設 ② `in.lammps` の `elements` オプションに名前を追記 ③ `qe_mdi_engine.py` の `pseudopotentials` に対応ポテンシャルを追加すれば準備OK！ |

これらを利用すれば、何度見返し、何プロジェクト回しても無限の効率・最高峰精度での計算活動をお約束いたします！
