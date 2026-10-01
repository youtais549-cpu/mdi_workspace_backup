# Goal Description
WSL上のローカル環境 (`~/research_simulations`) にて、LAMMPS と Quantum ESPRESSO を用いた MDI 連携シミュレーションを実行できるように環境構築を行います。システム領域への影響を避け、`sudo`（パスワード入力）なしで全自動インストールを行うための計画です。

## Open Questions
> [!IMPORTANT]
> `sudo` 権限が必要な `apt-get` の使用を避けるため、ユーザーのホームディレクトリに **Miniconda**（Pythonや関連ツールのパッケージ管理ソフト）をインストールし、その中に Quantum ESPRESSO やビルドツールを隔離してインストールする方針で進めてもよろしいでしょうか？（システム全体を汚さないため推奨される方法です）

## Proposed Changes

### 1. Miniconda の導入とセットアップ
- Miniconda のインストーラーをダウンロードし、`~/miniconda3` にサイレントインストールします。
- `conda` コマンドが使えるようにシェルを初期化します。

### 2. 依存パッケージと Quantum ESPRESSO のインストール
- `conda-forge` チャンネルを使用して以下をインストールします：
  - `quantum-espresso` (これで `pw.x` が使用可能になります)
  - `ase` (シミュレーションの連携用 Python ライブラリ)
  - `cmake`, コンパイラ群 (LAMMPSのビルド用)
- `pip` を用いて MDI 用の Python パッケージ `pymdi` をインストールします。

### 3. LAMMPS のソースコード取得とビルド（MDI有効化）
- 既存の `lmp` コマンドは MDI が有効になっていないため、LAMMPSのソースコードを GitHub から取得します (`~/research_simulations/lammps_src` などにクローン)。
- `CMake` を用いて、MDI パッケージを有効化 (`-DPKG_MDI=yes`) した状態でビルドを実行します。
- ビルドされた新しい `lmp` 実行ファイルをパスの通った場所 (`~/.local/bin/lmp` など) に配置し、既存のものと置き換えます。

## Verification Plan

### Automated Tests
- `which pw.x` および `pw.x --version` を実行し、Quantum ESPRESSO がインストールされたことを確認します。
- `lmp -h | grep MDI` を実行し、ビルドした LAMMPS で MDI サポートが有効になっていることを確認します。
- `python3 -c "import pymdi, ase"` を実行し、Python パッケージが正しく読み込めることを確認します。
