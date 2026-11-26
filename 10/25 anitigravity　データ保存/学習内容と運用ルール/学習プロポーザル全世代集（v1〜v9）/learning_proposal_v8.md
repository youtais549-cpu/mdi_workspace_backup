# Learning Proposal v8 — 指示書経由のグラフ自動生成定例化とモデル構築・先行バルクSCFプロトコル

> [!IMPORTANT]
> ユーザー様のご承認をいただくまで **ルール設定ファイルは変更していません**。下記の提案内容（採否・文言修正）をご確認ください。

---

## 1. 今回のセッションから抽出した学び

| # | 出来事 | 根本原因 | 再利用可能な教訓 |
|---|---|---|---|
| **A** | ユーザー様からのご提案：「3つのグラフを作成するという指示書の役割を果たすようなテキストファイルをアプリ上に作り、計算開始時に必ず経由して、指定した保存先へ自動保存されるように定例化したい」 | 従来は計算終了後に手動または別個のスクリプトでグラフを生成していたため、条件変更時や新フォルダ作成時にグラフ作成の呼び出し漏れや保存先パスの不一致が発生していた | **指示書テキストファイル（`RELAXATION_GRAPH_PROTOCOL.json`）と汎用自動生成エンジン（`auto_generate_progression_graphs.py`）を標準配備**し、すべての計算実行スクリプト（`run_colab_gpu.sh` 等）の完了処理に必ず組み込む。これにより、計算開始時に保存先フォルダ（`BACKUP_DIR`）を指定するだけで、計算終了時に一切の人手を介さず 100% 確実に 3 種の推移グラフが生成され、データと同じ Google Drive フォルダへ自動保存される。 |
| **B** | ユーザー様からのご確認：「モデルを作るときに既存の構造を上書きせずに新しくファイルをつくっていますか？」 | 周期数や真空層厚を変更する際、既存の構造データ（2周期、4周期等）や計算結果への意図せぬ上書き・消失に対するユーザーの懸念 | **「既存モデル・既存計算結果の完全非上書き原則」を再確認・厳格ルール化**。新モデル作成時は必ず専用の独立新規ディレクトリ（`calc_...`）および新規ファイル名（`bulk_...216atoms.*`, `slab_...216atoms.*`）を作成し、Google Drive 側にも新規専用フォルダを確立する。 |
| **C** | ユーザー様からの指示：「6周期の計算を始める前に、先に6周期でのバルクモデルのエネルギーを計算してください」 | 正確な表面破壊エネルギー $\gamma = \frac{E_{\text{slab}} - E_{\text{bulk}}}{2A}$ を算出するためには、スラブと完全に同数の原子数を持つバルク基準エネルギー $E_{\text{bulk}}$ の先行確定が不可欠 | **「バルク SCF 先行測定・確定の必須順序ルール」を策定**。スラブ構造緩和を開始する前に、必ず対応する原子数の真のバルクモデル（真空 0 Å）の 1 点 SCF 計算を実施し、$E_{\text{bulk}}$ の実測値および 1 原子あたりのエネルギー整合性（$\approx -443.49\text{ eV/atom}$）を検証・確定した上でスラブ計算に投入する。 |

---

## 2. 分類と更新方針

- **種別**: *Rule*（恒久ルールの改訂・追加）
- **更新対象**:
  1. [`/home/yamazaki/mdi_workspace_backup/AGENTS.md`](file:///home/yamazaki/mdi_workspace_backup/AGENTS.md)
     - §8「計算完了時の 3 種推移グラフ自動生成プロトコル」を【指示書テキストファイル経由の完全自動定例化システム】へ改訂・強化。
     - §1「計算結果の上書き防止と個別アーカイブ」に【バルク先行確定順序ルール】を明記。
  2. [`.agents/rules/colab_t4_gpu_aimd_workflow.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/colab_t4_gpu_aimd_workflow.md)
     - 計算実行パイプラインの標準フローに `auto_generate_progression_graphs.py` と指示書読込の必須化を追加。

---

## 3. 追記・改訂する具体的な文言（案）

### ① `AGENTS.md` §8 の改訂・強化（指示書経由の自動定例化）
```markdown
## 8. 指示書テキストファイル経由の 3 種推移グラフ自動生成・保存定例化システム（必須・恒久ルール）
- **指示書テキストファイル (`RELAXATION_GRAPH_PROTOCOL.json`) の必須配備**:
  ワークスペースルートおよび各計算ディレクトリに、3 種推移グラフの体裁（Word 8.0cm × 6.2cm, 600dpi, PNG/PDF/SVG, MS明朝 10.5pt, Times New Roman 9.5pt, 中抜き紫三角 `#8A2BE2`）を定義した指示書テキストファイルを常備すること。
- **汎用自動生成エンジン (`auto_generate_progression_graphs.py`) の連動**:
  計算実行スクリプト（`run_colab_gpu.sh`）の終了部（`wait $LMP_PID` 直後）には、必ず以下を組み込むこと：
  ```bash
  python3 auto_generate_progression_graphs.py
  ```
- **自動保存先解決ルール**:
  `auto_generate_progression_graphs.py` は、同ディレクトリの `master_run_gpu.sh` 内の `BACKUP_DIR`（Google Drive パス）を自動検出し、ローカル計算ディレクトリと Google Drive バックアップフォルダの両方へ即座に 3 種グラフ（①全エネルギー推移、③全原子作用力推移、④SCF補正値推移）を自動ダイレクト保存すること。手動操作や後付け生成に依存してはならない。
```

### ② `AGENTS.md` §1 への追記（バルク SCF 先行測定・確定ルール）
```markdown
- **スラブ緩和計算前の「バルク 1 点 SCF 先行確定」プロトコル（必須順序）**:
  新しい条件（周期数拡張など）でスラブ構造緩和計算を開始する前に、**必ず同一原子数の真のバルクモデル（真空層 0 Å）による Quantum ESPRESSO GPU 1 点 SCF 計算を先行実施**すること。
  - 実測されたバルク全エネルギー $E_{\text{bulk}}$ および 1 原子あたりのエネルギー（$-443.49\text{ eV/atom}$ 基準）の整合性を検証する。
  - 確定した $E_{\text{bulk}}$ を `fracture_metadata.json` に明記してからスラブ計算を開始すること。
```

---

## 4. 承認後の反映アクション
ユーザー様にご承認（「承認」「OK」等）をいただいた場合：
1. `AGENTS.md` を上記内容に改訂・更新します。
2. `.agents/rules/colab_t4_gpu_aimd_workflow.md` に標準パイプラインとして反映します。
3. すでに作成済みの [RELAXATION_GRAPH_PROTOCOL.json](file:///home/yamazaki/mdi_workspace_backup/RELAXATION_GRAPH_PROTOCOL.json) および [auto_generate_progression_graphs.py](file:///home/yamazaki/mdi_workspace_backup/auto_generate_progression_graphs.py) を永続運用環境として維持・同期します。
