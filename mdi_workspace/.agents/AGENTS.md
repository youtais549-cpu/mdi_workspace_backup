# LAMMPS + Quantum ESPRESSO MDI & Winmostar 統合ワークスペース・自動学習ルール (AGENTS.md)

このワークスペース (`~/mdi_workspace`) で活動するAIエージェントおよびユーザーは、以下のルール・既存環境とベストプラクティスに従うこと。

## 1. コアとなる構成と役割
- **MDI 結合シミュレーション仕様**:
  - LAMMPS (MDI Driver / TCP サーバーモード / ポート 8021 / `-hostname` なし) をバックグラウンドで立ち上げる。
  - ASE 経由で Quantum ESPRESSO (`pw.x`) をまわす Python 中継エンジン (`qe_mdi_engine.py`) を クライアントモード (`-hostname localhost`) で接続する。
  - 標準の `pw.x -mdi` はオプションを読まない仕様のため、必ず `qe_mdi_engine.py` をラッパーとして使用すること。

## 2. 新規シミュレーションプロジェクト（フォルダ）の展開テクニック
- 新しくプロジェクトを作る際は、手動でセットアップせず、必ずルート直下に作成した **自動構築スクリプト `init_project.sh`** を実行してフォルダ展開させること。
  ```bash
  cd ~/mdi_workspace
  ./init_project.sh <新規プロジェクトフォルダ名>
  ```
  ※これにより、必須の `run.sh`、`qe_mdi_engine.py`、`make_xyz.py`、擬似ポテンシャル `.upf`、テンプレート `in.lammps` が複製される。

## 3. シミュレーションの実行法
- 対象プロジェクトフォルダ内で、以下を一発叩くだけで LAMMPS/QE 双方向結合計算が実行される。
  ```bash
  ./run.sh
  ```

## 4. 可視化・Winmostar の取り扱いとトラジェクトリ変換 (最重要ルール)
- ユーザーから「計算結果を Winmostar 等で可視化したい」「アニメーションを見たい」とリクエストがあった場合、生の `dump.lammpstrj` （元素記号が入っていなくてファイル型誤認をおこす可能性があるため）を直接渡さず、**必ず `make_xyz.py` で標準 `.xyz` トラジェクトリ (Si, C 等の元素名補給済み) へ変換するよう促す**こと。
  ```bash
  python3 make_xyz.py  # => md_animation.xyz が作られる
  wm md_animation.xyz  # => Winmostar が立ち上がり即表示！
  ```
- **Winmostar 起動エイリアス (`wm`)**:
  - `~/.bashrc` 内に登録されている。Windows 側 ( `C:\winmos11\winmostar.exe` ) の Winmostar に、WSL 経路を `wslpath -w` で橋渡しして立ち上げるコマンドとして機能する。
  - コマンド一発：`wm md_animation.xyz` または `wm qe_mdi.pwo` を使う。
