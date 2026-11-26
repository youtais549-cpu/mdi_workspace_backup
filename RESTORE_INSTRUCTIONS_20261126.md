# 2H-SiC AIMD/MDI プロジェクト：データ移行・環境復元および Step 350 再開指示書 (2026-11-26)

本ドキュメントは、本リポジトリ（`mdi_workspace_backup`）を移行先環境（または初期化後の Antigravity IDE）へ展開した際、これまでの全学習ルール・会話履歴・計算成果物を 100% 復元し、一時停止した **8周期・真空層 5.0 Å・構造最適化なしスラブモデルの AIMD 計算（Step 350 完了時点）** を Step 351 からシームレスに再開するための指示書です。

---

## 1. リポジトリに含まれる全データ構成

- **恒久ルール・学習記憶**:
  - [`AGENTS.md`](AGENTS.md)（全 14 章、NAS 関連記述破棄済み最新版）
  - [`GEMINI.md`](GEMINI.md)（`AGENTS.md` への参照ポインタ）
  - `.agents/rules/` および `学習内容と運用ルール/`
- **会話ログ・レポートアーティファクト**:
  - `会話ログ/会話ログ_全履歴_20261126.txt`（本セッションの可読テキスト全履歴）
  - `会話ログ/raw_transcripts/transcript_cc114744-ec01-4b04-8765-40ec69ef7d2d.jsonl`（JSONL 完全トランスクリプト）
  - `会話ログ/brain_cc114744-ec01-4b04-8765-40ec69ef7d2d/`（全アーティファクト報告書・グラフ画像一式）
- **完了済み・一時停止中の主要 AIMD 計算ディレクトリ**:
  1. `aimd_2H-SiC_10-10_8periods_bulk_300K_300steps_rtx5080/`（8周期バルク 300 K AIMD: Step 0..300 完走）
  2. `aimd_2H-SiC_10-10_8periods_bulk_300K_600steps_rtx5080/`（8周期バルク 300 K AIMD: Step 0..600 完走）
  3. `aimd_2H-SiC_10-10_8periods_bulk_300K_900steps_rtx5080/`（8周期バルク 300 K AIMD: Step 0..900 完走）
  4. `aimd_2H-SiC_10-10_8periods_vac3.0A_300K_100steps_rtx5080/`（8周期・真空 3.0 Å 緩和済みスラブ: Step 0..100 完走）
  5. `aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080/`（8周期・真空 3.0 Å 未緩和スラブ: Step 0..100 完走）
  6. `aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_400steps_rtx5080/`（8周期・真空 3.0 Å 未緩和スラブ: Step 0..400 完走）
  7. **`aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080/`（8周期・真空 5.0 Å 未緩和スラブ: Step 350 完了時点で安全停止・全データ保存済み）**

---

## 2. Step 350 完了時点で保存されているデータ（真空層 5.0 Å・構造最適化なしスラブ）

[`aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080/`](aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080) 内に、Step 350 終了時点のすべての状態が完全保存されています：

- **位置座標・速度・熱浴内部状態**:
  - `restart.slab_vac5.0A_unrelaxed_step.350`（LAMMPS バイナリリスタートファイル）
  - `slab_10-10_288atoms_vac5.0A_unrelaxed_aimd_350steps_final.data`（Step 350 完了時点の構造・速度データファイル）
  - `dump.lammpstrj`（Step 0 〜 350 の全 351 フレーム座標・速度・原子力）
- **波動関数・電子密度・DFT エネルギー・原子力**:
  - `espresso_all_steps.pwo`（Step 0 〜 350 の全 351 ステップ分の Quantum ESPRESSO 完全出力）
  - `tmp/pwscf.save/charge-density.hdf5`（Step 350 収束済み電子密度）
  - `tmp/pwscf.save/wfc1.hdf5`（Step 350 収束済み波動関数、および GitHub 100 MB 制限対応の 45 MB 分割アーカイブ `wfc1.hdf5.gz.part_aa` 〜 `part_an` ＋ 復元スクリプト `restore_wfc1_hdf5.sh`）
- **Step 350 時点のアニメーション・統計データ・推移グラフ**:
  - `md_animation.xyz` / `md_nvt_animation.xyz`（351 フレーム Winmostar 用アニメーション）
  - `aimd_unrelaxed_vac5.0A_400steps_summary.csv` / `aimd_unrelaxed_vac5.0A_400steps_ensemble_stats.json`
  - Word 8.0cm 論文仕様推移グラフ一式（PNG / PDF / SVG）

---

## 3. 移行先での環境復元および Step 351〜400 再開手順

1. **計算環境（Micromamba + QE + LAMMPS-MDI）のセットアップ**:
   ```bash
   bash calc_2H-SiC_10-10_2periods_vac5A_local_RTX5080/setup_local_rtx5080_env.sh
   ```
2. **Step 350 波動関数ファイル（`wfc1.hdf5`）の復元（Git 経由でクローンした場合）**:
   ```bash
   bash aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080/tmp/pwscf.save/restore_wfc1_hdf5.sh
   ```
3. **Antigravity AI への再開指示**:
   移行後の Antigravity チャットにて以下のように指示してください：
   > 「`AGENTS.md` と `RESTORE_INSTRUCTIONS_20261126.md` を読み込んでください。`aimd_2H-SiC_10-10_8periods_vac5.0A_unrelaxed_300K_400steps_rtx5080` の Step 350 までの全データを引き継いで、残りの 50 ステップ（Step 351〜400）を再開してください。」
