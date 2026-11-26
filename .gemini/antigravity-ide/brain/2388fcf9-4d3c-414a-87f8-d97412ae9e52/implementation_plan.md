# Google Colab Pro (GPU + High-RAM) 移行と環境構築計画

Colab Proのハイメモリ＆GPU環境で、現在と同じ「LAMMPS + Quantum ESPRESSO (MDI結合)」のMD計算を実行できるようにするための環境構築プランです。

## User Review Required

> [!WARNING]
> Colabのインスタンスは切断されると初期化されるため、毎回環境構築（ソースからのコンパイル）を行うと数十分の無駄な時間がかかります。
> そのため、本プランでは**「初回のみコンパイルを行い、完成した実行ファイル（`pw.x` や `lmp`）をGoogle Driveに保存して、2回目以降はそれをコピーして即座に計算を開始する」**という設計のJupyter Notebookを作成します。

## Open Questions

> [!IMPORTANT]
> - Colab上で構築するQuantum ESPRESSOのバージョンは、現在ローカルで使われているもの（おそらくv7.2〜7.3付近）でよろしいでしょうか？（最新のNVIDIA HPC SDKと互換性のある安定版を使用します）
> - Colab（Jupyter Notebook）上で長時間MD計算を回す際、ブラウザを閉じても途切れないよう、ログをファイルに出力しながらバックグラウンド実行する仕組みを提供しますが、それでよろしいでしょうか？

## Proposed Changes

本計画では、以下のファイルをローカルに生成し、ユーザーがColabに持っていけるように準備します。

### 1. Colab用セットアップNotebookの作成
#### [NEW] `colab_setup_mdi_gpu.ipynb` (Colabで開くファイル)
Colabにアップロードして実行するためのJupyter Notebookファイルを作成します。以下のセルが含まれます：
- Google Driveのマウント
- Minicondaのインストールと `ase`, `pymdi` のセットアップ
- **NVIDIA HPC SDK** の導入と、GPU対応 Quantum ESPRESSO (`pw.x`) のコンパイル
- LAMMPS の MDI有効化ビルド
- コンパイル済みバイナリの Google Drive への退避（次回以降の時短用）
- テスト実行（3x3x2 などの軽いモデルでGPUが正しく動くか確認）

### 2. 計算用ファイルのパッケージ化
#### [NEW] `package_for_colab.sh`
現在の `SiC_3x3x10_MD` ディレクトリ一式を、Colab（Google Drive）へ簡単にアップロードできるように一つの ZIP ファイル (`colab_transfer.zip`) にまとめるスクリプトを作成・実行します。

### 3. Colab向け実行スクリプトの調整
#### [MODIFY] `SiC_3x3x10_MD/run.sh` -> `run_colab.sh`
現在の `run.sh` はローカル環境向け（例: `~/mdi_workspace/q-e/bin/pw.x` へのパス）になっているため、Colab上のパス（`/content/q-e/bin/pw.x` 等）に対応し、かつPythonのエラーも正しくログに残るように改良したColab用の実行スクリプトを追加します。

---

## Verification Plan

### Manual Verification
1. 提案承認後、私がZIPファイルとNotebookをローカルに生成します。
2. ユーザー側でNotebook (`colab_setup_mdi_gpu.ipynb`) と ZIPファイルを Google Drive にアップロードし、Colab Proで開いていただきます。
3. セルを上から順に実行し、エラーなく `pw.x` と `lmp` がビルドされること、および数ステップのMD計算がGPUを活用して高速に完了することを確認します。
