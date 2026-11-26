# /learn 学習提案書：安全中断・シームレス途中再開（Restart）プロトコルおよび 4周期（144原子）モデル実行基準の永続化

## 1. 提案の背景と学習内容の分類

今回の 2H-SiC $\{10\bar{1}0\}$ スラブモデルにおける **4周期（8層, 144原子）・真空層 5.0 Å** の第一原理構造緩和計算を通じて、以下の重要な運用ノウハウ・実行基準が実証・確立されました：

1. **4周期（144原子）大規模モデルの Tesla T4 GPU 実行基準**:
   - VRAM 約 8.75 GB / 15 GB で安定稼働、1ステップ所要時間 約 9.7 分、初期構造から約 $-360\text{ eV}$ の深層緩和を実証。
2. **Ubuntu 24.04 (noble) での NVHPC 24.7 必須化**:
   - `nvhpc-23-9` は依存関係エラー（`libncursesw5` 欠落）となるため、Ubuntu 24.04 では必ず `nvhpc-24-7` を使用すること。
3. **安全な計算中断と成果物二重保護**:
   - `killall -9 python3` を避け、`killall -9 pw.x.real pw.x lmp` および `pkill -f qe_mdi_engine` で Colab 接続（Jupyter/ngrok）を維持したまま安全停止。
   - 中断時点までの全軌道（45フレーム）を `make_xyz.py` で即座に Winmostar 用アニメーション `md_animation.xyz` に変換。
4. **シームレスな途中再開プロトコル（Continuation / Restart Protocol）**:
   - `dump.lammpstrj` の最終フレーム（最新の緩和原子座標）から、ボックス寸法・原子質量・原子種を完全に維持した再開用 LAMMPS データファイル（`slab_10-10_144atoms_restart.data`）を自動生成。
   - 再開用スクリプト（`in.lammps.restart`, `resume_run_gpu.sh`）を自動配備し、次回ワンコマンドで全く同一条件のまま続きから再開可能にする仕組み。

* **分類**: 既存ルールの更新（Update Existing Rules）
* **対象ファイル**:
  1. [`/home/yamazaki/mdi_workspace_backup/AGENTS.md`](file:///home/yamazaki/mdi_workspace_backup/AGENTS.md)
  2. [`/home/yamazaki/mdi_workspace_backup/.agents/rules/colab_t4_gpu_aimd_workflow.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/colab_t4_gpu_aimd_workflow.md)

---

## 2. 具体的な変更差分（Diff 案）

### ① `AGENTS.md` の更新

```diff
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -40,6 +40,23 @@
 - **自動バックアップ**:
   Colab 側 `/content/drive/MyDrive/MD_backup/` への 5 分間隔同期を維持すること。
 
+---
+
+## 8. 計算の安全中断とシームレス途中再開（Restart / Continuation）プロトコル（必須）
+- **安全停止手順**:
+  中断時は `killall -9 pw.x.real pw.x lmp` および `pkill -f qe_mdi_engine` を使用し、Colab の Jupyter / SSH 接続を維持すること。
+- **途中経過アニメーション化**:
+  停止直後に必ず `python3 make_xyz.py dump.lammpstrj md_animation.xyz` を実行し、Winmostar で途中までの緩和挙動を確認可能にすること。
+- **最新座標からの再開データ生成**:
+  `dump.lammpstrj` の最終フレーム（最新 Timestep）から、ボックス寸法・原子ID・Type・質量を維持した再開用データファイル（`slab_*_restart.data`）を自動抽出し、`in.lammps.restart` およびワンクリック再開スクリプト `resume_run_gpu.sh` を配備すること。
+
+---
+
+## 9. 周期数（厚み）拡張モデル（4周期 8層 144原子）の実行基準
+- **システム規模とVRAM消費**:
+  4周期 8層 144原子モデル（$3\times 3\times 4$）は Tesla T4 GPU（VRAM 15 GB）において実測約 8.75 GB を消費し、1ステップあたり約 9.7 分（約 580 秒）で安定動作する。
+- **臨界真空層厚さ**:
+  非極性 $\{10\bar{1}0\}$ 面では 5.0 Å でスラブ間相互作用が完全に遮断されるため、4周期モデルでも真空層は 5.0 Å（上下各 5.0 Å）を採用する。
```

---

### ② `.agents/rules/colab_t4_gpu_aimd_workflow.md` の更新

```diff
--- a/.agents/rules/colab_t4_gpu_aimd_workflow.md
+++ b/.agents/rules/colab_t4_gpu_aimd_workflow.md
@@ -24,8 +24,10 @@
   * 360原子モデルは Colab のメインメモリ（RAM > 13.15 GB）不足により OOM クラッシュするため禁止。
   * 72原子モデル（$3\times 3\times 2$, カットオフ 40 Ry / 320 Ry）を採用すること（Tesla T4 15GB VRAM のうち実測約 9.4 GB を消費、GPU使用率 95%、43〜49W P0状態で高速・安定動作。所要時間は Step 0 初期収束約 7.5分、以降約 5〜7分/ステップ）。
+  * 144原子モデル（4周期 8層, $3\times 3\times 4$）: Tesla T4 GPU で VRAM 実測約 8.75 GB を消費、1ステップあたり約 9.7 分で高速・安定動作可能。
 * **対角化並列化設定**:
   * 単一 T4 GPU での実行時は、必ず `pw.x -ndiag 1` を指定すること（マルチGPU用スケーリングオーバーヘッドを回避）。
+* **Ubuntu 24.04 での NVHPC バージョン**:
+  * Ubuntu 24.04 (noble) では `nvhpc-23-9` が依存関係（`libncursesw5`）によりインストールできないため、必ず `nvhpc-24-7` を使用すること。
 
 ---
 
@@ -113,6 +115,22 @@
 
 ---
 
+## 8. 計算の安全中断とシームレス途中再開（Restart）規約
+長時間計算を途中で中断する場合、次回全く同一条件で継続できるよう以下の手順を厳守すること：
+1. **プロセスの安全停止**:
+   `killall -9 pw.x.real pw.x lmp 2>/dev/null || true`
+   `pkill -f qe_mdi_engine 2>/dev/null || true`
+2. **途中経過 XYZ の自動生成**:
+   `python3 make_xyz.py dump.lammpstrj md_animation.xyz` を実行。
+3. **最新緩和フレームの抽出と再開データファイル生成**:
+   `create_restart_structure.py` を用いて、`dump.lammpstrj` の最終 Timestep から `slab_*_restart.data` を生成。
+4. **再開スクリプトの配備**:
+   `in.lammps.restart`（`read_data slab_*_restart.data`、`dump_modify append yes`）および `resume_run_gpu.sh` を作成・配備。
+5. **次回再開コマンド**:
+   Colab 側で `bash resume_run_gpu.sh` を実行するだけで、中断した最新構造からシームレスに計算を続行可能にする。
+
+---
+
 ## 9. リアルタイム計算監視プロトコル (Real-Time Monitoring)
 Colab 上での長時間の QE / LAMMPS 計算進行中、Antigravity IDE 上からリアルタイムに進捗を把握できるよう、以下のツールを標準維持すること：
```
