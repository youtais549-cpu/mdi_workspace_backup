# モジュール型 第一原理MD (LAMMPS + Quantum ESPRESSO) 表面破壊エネルギー解析基盤

本パッケージは、2H-SiC の表面破壊エネルギー $\gamma = \frac{E_{\text{slab}} - E_{\text{bulk}}}{2A}$ を評価するための、パラメータ可変型シミュレーションフレームワークです。

## フォルダ構成
* **[parameters_variable/](file:///home/yamazaki/mdi_workspace_backup/modular_aimd_framework/parameters_variable/)**: 研究条件（真空層厚さ、周期数、結晶面、DFT条件、計算モード）を変更する際に編集・操作するフォルダ。
* **[core_unchanging/](file:///home/yamazaki/mdi_workspace_backup/modular_aimd_framework/core_unchanging/)**: MDI通信、T4 GPU最適化、Google Colabバックグラウンド実行・Google Drive自動バックアップなどを司る固定コアエンジン群（編集不要）。
* **[CONFIG_GUIDE.md](file:///home/yamazaki/mdi_workspace_backup/modular_aimd_framework/CONFIG_GUIDE.md)**: 各パラメータ変更時の対応表と具体的な手順書。

## 基本的な研究ワークフロー
1. `parameters_variable/model_settings.py` で計算条件（真空層・周期数・結晶面など）を指定。
2. `python3 parameters_variable/generate_models.py` を実行してスラブおよびバルク構造を一括生成。
3. `python3 core_unchanging/workflow_cli.py upload parameters_variable` で Colab へ転送。
4. 計算完了後、`python3 parameters_variable/calc_surface_energy.py <E_slab> <E_bulk>` で表面破壊エネルギー $\gamma$ [J/m²] を自動算出。
