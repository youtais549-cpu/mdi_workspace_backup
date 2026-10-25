# 学習提案書 (Learning Proposal): ワークスペース運用ルールの総合更新（第3版）

直近のやり取り（縦軸スケールの微小変化識別化、DFTノイズ限界とLAMMPS緩和停止基準の乖離による早期完了判定プロトコル）に基づき、以下の恒久的なルール更新を反映・完了いたしました。

---

## 1. 学習対象の分類と選定理由

- **分類**: **既存ルールの更新 & 早期完了判定プロトコルの確立 (Update Existing Rules & Early Termination Protocol)**
- **対象ファイル**:
  1. [`.agents/rules/surface_fracture_slab_rules.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/surface_fracture_slab_rules.md)
  2. [`AGENTS.md`](file:///home/yamazaki/mdi_workspace_backup/AGENTS.md)
  3. [`GRAPH_STYLE_SPEC.md`](file:///home/yamazaki/mdi_workspace_backup/GRAPH_STYLE_SPEC.md)
  4. [`generate_final_graph.py`](file:///home/yamazaki/mdi_workspace_backup/generate_final_graph.py)
- **選定理由**:
  - **微小変化の視覚的識別化**: 表面破壊エネルギーの真空層依存性（$\Delta \gamma \approx 0.02\text{ J/m}^2$）を誰が見ても一目で判別できるようにするため、縦軸スケールを $2.4 \sim 3.2\text{ J/m}^2$（0.1 刻み）に標準化。
  - **第一原理構造緩和の早期完了判定**: DFT の数値ノイズフロア（$\sim 0.0002\text{ Ry/au} \approx 0.006\text{ eV/\AA}$）により LAMMPS の `ftol = 1.0e-3 eV/Å` を満たさず長時間回り続ける現象に対し、「全エネルギー固定」「原子完全静止」「Total force停滞」を検知して安全に早期完了させる判断基準を明文化。

---

## 2. 反映完了したルール更新内容

### (1) `surface_fracture_slab_rules.md`
- **第9章 (早期完了判定プロトコル)**:
  - DFT 数値ノイズフロア（$\approx 0.0002\text{ Ry/au}$）の物理的背景を記録。
  - 「全エネルギー小数第4位固定」「原子最大移動量 $\le 10^{-6}\text{ \AA}$」「Total force 停滞」の 3 条件成立時、直ちに計算を正常終了・成果物確定へ移行するルールを追加。
- **第10章 (論文・報告書向けプロ仕様グラフ標準)**:
  - 縦軸範囲: $2.4 \sim 3.2\text{ J/m}^2$
  - 縦軸目盛り: `2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2` (0.1 刻み)
  - プロット点: 中抜き紫三角マーカー（`marker='^'`, `facecolors='none'`, `#8A2BE2`, `s=70`, `linewidths=1.6`）

### (2) `AGENTS.md`
- コアガイドライン第6項に「スラブCG緩和の早期完了判定プロトコル」を明記。
- 第7項に縦軸 2.4〜3.2（0.1刻み）および中抜き紫三角マーカーの厳格仕様を反映。

### (3) `GRAPH_STYLE_SPEC.md` & `generate_final_graph.py`
- スクリプトおよび仕様書を縦軸 2.4〜3.2（0.1刻み）に更新し、Google Drive にも同期完了。
