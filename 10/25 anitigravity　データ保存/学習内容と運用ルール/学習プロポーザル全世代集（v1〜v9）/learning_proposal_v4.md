# 学習提案書 (Learning Proposal): ワークスペース運用ルールの総合更新（第4版）

直近のやり取り（4周期144原子モデルにおける極小点底の早期完了判定の定量的基準、過去3計算および今後の新計算に対する 3 種類の推移グラフ自動作成・保存の標準化）に基づき、以下の恒久的なルール更新を反映・完了いたしました。

---

## 1. 学習対象の分類と選定理由

- **分類**: **既存ルールの更新 & 必須プロトコルの追加 (Update Existing Rules & Add Mandatory Protocols)**
- **対象ファイル**:
  1. [`AGENTS.md`](file:///home/yamazaki/mdi_workspace_backup/AGENTS.md)
  2. [`.agents/rules/surface_fracture_slab_rules.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/surface_fracture_slab_rules.md)
  3. [`.agents/rules/colab_t4_gpu_aimd_workflow.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/colab_t4_gpu_aimd_workflow.md)
  4. Google Drive 側 [`/content/drive/MyDrive/MD_backup/AGENTS.md`](file:///content/drive/MyDrive/MD_backup/AGENTS.md)
- **選定理由**:
  - **系の大型化に伴う早期完了判定の定量的基準の確立**:
    原子数が倍増（72原子 $\to$ 144原子）したことで、DFT（QE）の数値ノイズフロア（$\sim 0.0002\text{ Ry/au} \approx 0.006\text{ eV/\AA}$）により、LAMMPS の `ftol = 1.0e-3 eV/Å`（$= 0.001\text{ eV/\AA}$）が永遠に満たされない現象がより顕著になることが判明。「極小点の底に達してから何ステップ変わらなければ終了してよいか」の定量的基準（連続 3〜5 回の評価で $\Delta E < 0.1\text{ eV}$ かつ 1原子あたり $< 1\text{ meV}$）を明文化。
  - **計算完了時の 3 種推移グラフ自動作成プロトコルの恒久化**:
    ユーザー様からの明示的なご指示により、今後のすべての構造緩和計算（新規面方位、異なる層数、異なる真空厚等）において、計算終了時に直ちに ①全エネルギー推移、③全原子作用力推移、④SCF補正値推移 の 3 種類の推移グラフ（Word配置用 8.0 cm 幅、MS明朝・Times New Roman、中抜き紫三角マーカー、文献値点線なし）を自動生成し、ローカルおよび Google Drive（`G:\マイドライブ\MD_backup\<計算名>\`）に完全格納するルールを絶対遵守事項として設定。

---

## 2. 反映完了したルール更新内容

### (1) `AGENTS.md`
- **第6項 (早期完了判定プロトコル) の定量的基準の強化**:
  - 自由度倍増による統計的ノイズ蓄積の物理的背景を記録。
  - 連続 3〜5 回の力評価でエネルギー改善が頭打ち（$\Delta E < 0.1\text{ eV}$ / 1原子あたり $< 1\text{ meV}$）かつ原子静止（$\Delta r_{\max} \le 10^{-6}\text{ \AA}$）を確認した場合、直ちに構造緩和 100% 完了と判定して安全停止・成果物確定へ移行する基準を明記。
- **第8項 (計算完了時の 3 種推移グラフ自動生成プロトコル) の新設**:
  - 緩和完了時に必ず以下の 3 種類の推移グラフ（PNG 600 dpi, PDF, SVG）を自動生成し、ローカルおよび Google Drive に保存することを義務化：
    1. **① 全エネルギー推移グラフ (`Total_Energy_progression.*`)**: 縦軸 `系全体のエネルギー [eV]`, 横軸 `構造緩和ステップ数 [Step]`
    2. **③ 全原子作用力推移グラフ (`Total_Force_progression.*`)**: 縦軸 `Total force [Ry/au]`, 横軸 `構造緩和ステップ数 [Step]`
    3. **④ SCF 補正値推移グラフ (`Total_SCF_Correction_progression.*`)**: 縦軸 `Total SCF correction [Ry/au]`, 横軸 `構造緩和ステップ数 [Step]`
  - 体裁仕様: 横 8.0 cm × 縦 6.2 cm、MS明朝 10.5 pt、Times New Roman 9.5 pt、数式 STIX、中抜き紫三角マーカー（`#8A2BE2`, `s=45`, `lw=1.2`）＋折れ線、4辺枠線、内向き目盛り、文献値点線なし。

### (2) `.agents/rules/surface_fracture_slab_rules.md`
- **第9章 (早期完了判定基準)** に、連続 3〜5 ステップ停滞の定量的クライテリアを追加。
- **第11章 (Mandatory Progression Graph Suite)** を新設し、計算終了処理（Fix）の一環として自動的に 3 種推移グラフを作成・配置するよう標準化。

### (3) Google Drive ディレクトリ標準命名規則の統一
- `{101_0}2周期10Å\`
- `{101_0}2周期5Å\`（全角・半角双方を維持）
- `{101_0}2周期2.5Å\`
- `[101_0]4周期５Å\`
各フォルダに計算スクリプト、出力ログ、Winmostar アニメーション、および 3 種推移グラフが完全同期されている状態を維持。

---

## 3. 今後の運用方針
次回の計算（層数拡張モデルや異なる結晶面）を開始する際、エージェントは：
1. 計算開始時から終了判定までをこの定量的ノイズフロア基準で監視し、無駄な GPU 時間の浪費を防止します。
2. 計算終了時、人手を介さずに自動的に上記 3 種類の推移グラフ（高解像度 PNG, PDF, SVG）を各計算フォルダに完全出力・同期します。
