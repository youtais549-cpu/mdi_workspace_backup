# LAMMPS + Quantum ESPRESSO (MDI) NVTシミュレーション環境構築プラン

真空層を追加した3×3×10のSiCモデルを用いて、LAMMPSとQuantum ESPRESSOを連携（MDI）させたNVTアンサンブルでの分子動力学計算環境を構築します。

## 構築ステップ

1. **新規プロジェクトの作成**
   `init_project.sh` スクリプトを使用して、新しい計算ディレクトリ `SiC_3x3x10_MD` を作成し、実行に必要なテンプレートスクリプト（`run.sh`, `qe_mdi_engine.py`, `in.lammps`, `.upf`ファイル等）を一括コピーします。

2. **モデルデータの変換**
   先ほど真空層を追加した `SiC_3x3x10_QE_only/qe.in` の構造データを読み込み、ASE（Atomic Simulation Environment）を用いてLAMMPS用のデータファイル（`SiC_3x3x10_vacuum.data`）に変換・出力し、新ディレクトリに配置します。

3. **LAMMPS入力スクリプト(`in.lammps`)の更新**
   - 読み込むデータファイルを `SiC_3x3x10_vacuum.data` に変更します。
   - アンサンブルをNVEからNVTに変更します：
     ```diff
     - fix 2 all nve
     + fix 2 all nvt temp 300.0 300.0 0.1
     ```

## User Review Required

> [!IMPORTANT]
> 温度はとりあえず室温（300.0 K）で設定していますが、もしターゲットとする設定温度や、シミュレーション時間（ステップ数）に変更が必要な場合はお知らせください。

問題がなければ「Proceed」ボタンを押して実行を許可してください。実行後、すぐに計算を開始できるように準備を完了させます。
