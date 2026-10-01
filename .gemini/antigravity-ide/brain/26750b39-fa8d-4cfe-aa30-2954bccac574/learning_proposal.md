# 学習提案書 (Learning Proposal): LAMMPS-QE MDI 結合 MD & Winmostar 可視化スキル

本セッションにおける不具合解決ならびに環境構築の経験を分析し、今後のやり取りでAIが一切の迷い・エラーなく適切に対応・再現できるよう、以下のカスタムスキル (Skill) としてシステムへの登録・永続保存を提案します。

---

## 1. 学習対象の選定と理由 (Rationale)
- **問題と達成ポイント**:
  1. 標準ビルドされた `pw.x` が MDI の通信ポート引数を処理できずにスタンドアローン動作してしまう現象（ソケットハング）に対し、**Python + ASE + pymdi による中継エンジン (`qe_mdi_engine.py`) をサーバー／クライアントの正しい TCP 設定で統合運用**する解法が完全に確立・検証されたこと。
  2. LAMMPS のシミュレーションデータを Windows 版 Winmostar V11（WSL 経由）で可視化するにあたり、生の `.lammpstrj` の自動誤検知を未然に防ぎ、元素（Si, C 等）の色分け・構造を100%確実かつ 1 秒で描画する **`.xyz` 多段動画変換 ＆ `wm` (wslpath 変換) エイリアスの実戦手法**が見出されたこと。

これらは領域特化型（科学・シミュレーション領域）の高精細ツール＆コマンド連携パターンであり、「カスタムスキル (Skill)」としての保存が最適です。

---

## 2. 実装予定のカスタムスキル構成

**配置先計画**: `~/mdi_workspace/.agents/skills/lammps_qe_mdi/SKILL.md` (および `~/.gemini/config/skills` などの全グローバルスキルへ同時適合可能)

### SKILL.md の内容

```markdown
---
name: LAMMPS and Quantum ESPRESSO MDI Coupled MD Simulation and Winmostar Visualization
description: Best practices and command workflows for LAMMPS + Quantum ESPRESSO on-the-fly MDI coupling MD in Linux/WSL, folder setup via init_project.sh, and trajectory visualization in Winmostar on Windows.
---

# LAMMPS + Quantum ESPRESSO MDI Coupling & Winmostar Visualization Master Skill

このスキルは、LAMMPS を古典・第一原理結合分子動力学 (MD) のドライバーとして扱い、Quantum ESPRESSO (pw.x) を力とエネルギー算出エンジン (QM/MM・オンザフライ第一原理計算) として実行および解析可視化する際に自動適用すること。

## 1. コアシステム構成 (TCP Server & Client Model)
- **直接の `pw.x -mdi` は使用禁止**: MDI未対応の pw.x は引数を読み飛ばし、LAMMPS をソケット待ちでハングアップさせるため。
- **必ず ASE ＋ 中継スクリプト (`qe_mdi_engine.py`) を使用する**:
  - **LAMMPS側 (サーバー / ドライバー)**: 
    `-role DRIVER -name LAMMPS -method TCP -port 8021` （※`-hostname localhost` は入れないこと！）
  - **Python中継側 (クライアント / エンジン)**:
    `python3 qe_mdi_engine.py -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost"`

## 2. 新規シミュレーションフォルダーの作成テクニック
- 新たなパラメータ・温度などで新規プロジェクト（新フォルダ）を起こす際は、手動設定ではなく `~/mdi_workspace/init_project.sh <新フォルダ名>` を実行させる。これにより必須の `run.sh`、`make_xyz.py`、擬似ポテンシャル(.upf)、テンプレートファイルがすべて完全設定で配備される。

## 3. Quantum ESPRESSO 側の SCF 収束・振動防止のお約束 (input_data)
- オープンシェルや変位状態でも SCF 反復発散（100回停止）を起こさせないため、ASE 経由での設定辞書に以下を必須で盛り込むこと：
  ```python
  'system': {'ecutwfc': 40.0, 'occupations': 'smearing', 'smearing': 'gaussian', 'degauss': 0.01},
  'electrons': {'conv_thr': 1.0e-5, 'mixing_beta': 0.3, 'mixing_ndim': 10, 'electron_maxstep': 200},
  'control': {'tprnfor': True, 'tstress': True, 'disk_io': 'minimal'}
  ```
- ファイル衝突を防ぐため、Espresso オブジェクト生成時は常に `label='qe_mdi'` を指定し、`command='... -in qe_mdi.pwi > qe_mdi.pwo'` を同期させる。
- LAMMPS側 (`in.lammps`) でも `fix 1 all mdi/qm elements Si C` のように明示的に元素名を宣言すること。

## 4. 究極の Winmostar 可視化ワークフロー (WSL -> Windows 連携)
- ユーザーから Winmostar での結果確認を依頼された際、生の `dump.lammpstrj` （元素名不記載による読取判定エラーを招く可能性がある）をそのまま扱わず、**必ず元素付きの標準 `.xyz` トラジェクトリへ変換した上で呼び出すこと**。

**実践ステップ**:
1. 変換実行: `python3 make_xyz.py` (=> `md_animation.xyz` を一撃で出力)
2. 可視化呼び出し: `wm md_animation.xyz` (または QE 計算ログなら `wm qe_mdi.pwo` や `wm espresso.pwi` でも即起動可)
3. (`wm` コマンドは `~/.bashrc` にセットされた `/mnt/c/winmos11/winmostar.exe "$(wslpath -w $1)" &` を利用するエイリアス関数であること。)
```

---

## 3. 承認後の更新プロセス
お客様の「**Proceed (承認・続行)**」をいただいた後に、上記 SKILL 情報をワークスペース環境のカスタムスキルルート ( `.agents/skills/lammps_qe_mdi/SKILL.md` ) ならびに永続ファイル構造に反映・登記いたします！
