# 学習提案書 (Learning Proposal): ワークスペース運用ルールの総合更新（第2版）

直近のやり取り（真空層厚さ 10 Å・5 Å・2.5 Å の比較実験、極薄真空層における CG 構造緩和の収束診断、論文・報告書向けグラフ体裁仕様のユーザー承認）に基づき、以下の恒久的なルール更新を提案・適用します。

---

## 1. 学習対象の分類と選定理由

- **分類**: **既存ルールの更新 & 新規プロトコルの追加 (Update Existing Rules & Protocols)**
- **対象ファイル**:
  1. [`.agents/rules/surface_fracture_slab_rules.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/surface_fracture_slab_rules.md)
  2. [`.agents/rules/colab_t4_gpu_aimd_workflow.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/colab_t4_gpu_aimd_workflow.md)
  3. [`AGENTS.md`](file:///home/yamazaki/mdi_workspace_backup/AGENTS.md)
  4. [`GRAPH_STYLE_SPEC.md`](file:///home/yamazaki/mdi_workspace_backup/GRAPH_STYLE_SPEC.md)（新規仕様書として保存済み）
- **選定理由**:
  - **真空層依存性の臨界値の明文化**: 2H-SiC $\{10\bar{1}0\}$ において「5.0 Å 以上で相互作用が完全遮断され、2.5 Å で微小な相互作用が検知される」という重要な物理的知見を恒久記録するため。
  - **極薄真空層の緩和診断プロトコル**: ポテンシャル曲面がフラットな系でラインサーチが多数回行われる際、発散ではなく正常な極小点静止状態（`atom move = 0.000000 Å`）であることを正しく診断できるようにするため。
  - **グラフ体裁の厳格仕様化**: ユーザーに承認いただいた高品質グラフ体裁（Times New Roman, 14.5pt, 原点0.0縦軸共用, 文献値太字等）を今後の全グラフ作成に適用するため。

---

## 2. 提案する更新内容

### (1) `surface_fracture_slab_rules.md` への追加（第8章・第9章の新設）

```markdown
## 8. Vacuum Layer Thickness & Interaction Cutoff Threshold
- **Benchmark Findings (2H-SiC {10-10} Slab)**:
  - **10.0 Å (total vacuum 20.0 Å)**: $E_{\text{slab}} = -31,892.6375\text{ eV} \implies \gamma = 2.4488\text{ J/m}^2$.
  - **5.0 Å (total vacuum 10.0 Å)**: $E_{\text{slab}} = -31,892.6430\text{ eV} \implies \gamma = 2.4485\text{ J/m}^2$ ($\Delta \gamma = 0.0003\text{ J/m}^2$, 完全遮断).
  - **2.5 Å (total vacuum 5.0 Å)**: $E_{\text{slab}} = -31,892.2630\text{ eV} \implies \gamma = 2.4703\text{ J/m}^2$ ($\Delta \gamma \approx +0.0218\text{ J/m}^2$, 表面間相互作用を検知).
- **Critical Cutoff Guideline**:
  - 2H-SiC $\{10\bar{1}0\}$ における相互作用遮断の臨界真空層厚さは **$2.5\text{ \AA} \sim 5.0\text{ \AA}$**（片側厚さ）である。5.0 Å 以上あれば計算コストを抑えつつ十分な遮断精度が得られる。

## 9. Convergence Diagnostic Protocol for Ultra-Thin Vacuum Slabs
- **Flat Potential Energy Surface & Line Search Behavior**:
  - 真空層が極薄（2.5 Å等）の場合、対向スラブの電子雲干渉によりエネルギー面の底が極めて平坦になり、DFT の数値ノイズ（$0.1 \sim 1\text{ meV}$）領域で CG 法のラインサーチ歩幅 $\alpha$ 縮小探索が多数回（約 100 回）発生する。
- **Diagnostic Criteria**:
  - エージェントは単にステップ数だけで判断せず、`dump.lammpstrj` の主ステップ間変位量およびエネルギー推移を確認すること。
  - 全原子の最大移動量が $0.000000\text{ \AA}$（完全静止）かつエネルギーが小数第 4 位まで一定であれば、**完全に最安定点に収束しており、`linesearch alpha is zero` による正常終了待機状態である** と診断すること。
```

---

### (2) `surface_fracture_slab_rules.md` への追加（第10章：グラフ作成標準）

```markdown
## 10. Publication-Quality Plotting Standards
When generating comparison graphs for surface fracture energy vs. vacuum thickness:
1. **Aspect Ratio & Figure Size**: Rectangular (8.0 × 5.2 inches, dpi=300).
2. **Axis Labels**:
   - Y-axis: `表面破壊エネルギー [$\mathrm{J/m^2}$]` (14.5 pt, Units in Times New Roman).
   - X-axis: `真空層の厚さ [$\mathrm{\AA}$]` (14.5 pt, Units in Times New Roman).
3. **Ticks & Origin Formatting**:
   - Ticks: Times New Roman, 12.5 pt, direction='in'.
   - Origin (0, 0): Do NOT duplicate "0.0". Keep Y-axis "0.0" and suppress/mask the X-axis left-end "0.0".
4. **Data Plotting**: Solid circles (`s=60`), points only (NO connecting lines).
5. **Literature Reference Line**:
   - Horizontal dashed line (`ls='--'`, `lw=1.2`, `alpha=0.85`).
   - Label: Bold Japanese `文献値` + Times New Roman Bold `(3.03 J/m²)`, 11.5 pt.
6. **Font Fallback**: `Times New Roman` for English/numbers/math, `Noto Sans CJK JP` or `IPAGothic` for Japanese.
```

---

### (3) `AGENTS.md` の更新
コアガイドラインに「真空層臨界厚さ（2.5〜5.0 Å）」「極薄真空層の収束診断プロトコル」「承認済みプロフェッショナルグラフ仕様の順守」を明記。
