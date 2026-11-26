# Learning Proposal v10 — 新環境（WSL / Antigravity IDE）における拡張機能・表示言語反映手順とルール正本統一

> [!NOTE]
> ユーザー様のご承認（2026-11-05）に基づき、[`AGENTS.md`](../AGENTS.md)、[`GEMINI.md`](../GEMINI.md)、および復旧指示書へ反映完了済みです。

---

## 1. 今回のセッションから抽出した学び

| # | 出来事・発見 | 根本原因 | 再利用可能な教訓 |
|---|---|---|---|
| **A** | **新環境（`WORKSTATION4WSL`）での拡張機能・表示言語の反映確認**<br>[`.vscode/extensions.json`](../.vscode/extensions.json) に13種の推奨拡張機能があるが、WSL環境での有効化状況や日本語パックの再起動反映手順の確認が必要だった。 | `.vscode/extensions.json` は推奨リスト定義であり、WSL 接続時は「WSL: Ubuntu」側への拡張機能導入および `Configure Display Language` からの再起動が別途必要となるため。 | 新環境移行マニュアルおよび運用ルール（`AGENTS.md` §11）に、**WSL リモート側での拡張機能（Python, Pylance, C/C++, LAMMPS）有効化確認**と、**表示言語切替（`Ctrl+Shift+P` → `Configure Display Language` → `日本語 (ja)` → 再起動）** の手順を明記する。 |
| **B** | **ワークスペース直下の `AGENTS.md` と `GEMINI.md` の二重読込解消**<br>同一内容（15,113 bytes）の `AGENTS.md` と `GEMINI.md` が両方存在し、システムプロンプトに同じ全文が 2 回重複注入されていた。 | 移行時に両方のファイル名で同じルールを配置したため、Antigravity のディレクトリルール自動探索が両方を読み込んでいた。 | ルール更新時の一貫性維持とコンテキスト枠（Rules Budget 20,000 tokens）の節約のため、正本を [`AGENTS.md`](../AGENTS.md) に統一し、[`GEMINI.md`](../GEMINI.md) は正本への参照ポインタとする。 |

---

## 2. 分類と更新対象

- **種別**: *Rule*（恒久ルールの拡充・最適化）
- **更新ファイル**:
  1. [`AGENTS.md`](../AGENTS.md)（§11 の新設、およびバックアップ先 `学習内容と運用ルール/AGENTS.md` への同期）
  2. [`GEMINI.md`](../GEMINI.md)（重複注入防止のため [`AGENTS.md`](../AGENTS.md) への参照ポインタ化）
  3. [`RESTORE_INSTRUCTIONS_20261025.md`](../RESTORE_INSTRUCTIONS_20261025.md)（Step 3 に拡張機能・表示言語反映手順を追記）
