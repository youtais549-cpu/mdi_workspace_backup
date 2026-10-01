# LAMMPS + Quantum ESPRESSO (MDI) Local Environment Setup

`research_simulations` (WSL) 上で、MDIを用いたLAMMPSとQuantum ESPRESSO連携シミュレーションを実行するための環境構築が完了しました。システム環境（`sudo`）に影響を与えないセキュアな設計でセットアップを完了しています。

## 構築された環境

- **Miniconda**: `~/miniconda3` に独立したPythonおよびパッケージ管理環境を導入しました。
- **Quantum ESPRESSO**: Conda経由でインストールされ、`pw.x` 等が使用可能になっています。
- **LAMMPS**: GitHubの最新安定版ソースコードを `~/research_simulations/lammps_src` にクローンし、MDIパッケージを有効にした状態でビルドしました。実行ファイルは `~/miniconda3/bin/lmp` に配置済みです。
- **Python モジュール**: ASE および MDI の通信に必要な `pymdi` (モジュール名: `mdi`) を導入しました。

## 実行方法

今後の計算では、専用のConda環境内でツール群を呼び出す必要があります。計算を実行するシェルで事前に以下のコマンドを実行するか、スクリプト（`run.sh` など）の先頭に追記してください。

```bash
# 環境の有効化（必須）
source $HOME/miniconda3/bin/activate

# 実行例
./run.sh
```

> [!TIP]
> ターミナルを起動するたびに自動で環境を有効にしたい場合は、`~/.bashrc` に `source $HOME/miniconda3/bin/activate` を追記すると便利です。

> [!NOTE]
> `pymdi` パッケージのインポート名は `mdi` となります（スクリプト内で `import mdi` と記述します）。既存の `qe_mdi_engine.py` で正しく参照できるようになっています。
