# Google Colab への環境移行ガイド

Google Colab Pro (GPU + High-RAM環境) で現在の `SiC_3x3x10_MD` の計算を実行するためのファイル準備が完了しました。

## 用意されたファイル
以下の2つのファイルをGoogle Driveにアップロードしてください。
1. **[colab_setup_mdi_gpu.ipynb](file:///home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb)**: 環境構築用のJupyter Notebook
2. **[colab_transfer.tar.gz](file:///home/yamazaki_yuta/mdi_workspace/colab_transfer.tar.gz)**: 計算実行に必要なファイル一式（入力データ・スクリプト類）

## Colabでの実行手順

> [!IMPORTANT]
> Colabのインスタンスはランダムで切断されるため、本Notebookは「**コンパイルした実行ファイルをGoogle Driveに保存し、次回以降はコンパイルをスキップして時短する**」仕組みになっています。

### Step 1: ファイルのアップロード
- ご自身のGoogle Driveのマイドライブ直下に `colab_transfer.tar.gz` をアップロードします。
- `colab_setup_mdi_gpu.ipynb` をGoogle Driveにアップロードし、Google Colaboratoryで開きます。

### Step 2: 環境構築セルの実行
- Colabのメニューから「ランタイム」>「ランタイムのタイプを変更」を選択し、**ハードウェア アクセラレータを「GPU」**（可能ならA100またはV100）、**システムRAMを「ハイメモリ」**に設定して保存します。
- Notebookのセルを上から順番に実行していきます。
  - 最初のセルでGoogle Driveのマウント許可が求められます。
  - Nvidia HPC SDKのインストールには5〜10分程度かかります。
  - QE（`pw.x`）とLAMMPS（`lmp`）のコンパイルが完了すると、自動的にGoogle Drive（`MyDrive/mdi_binaries/`）にバックアップ保存されます。

### Step 3: 計算の開始
最後のセルまで実行してパス設定が終わったら、Colab内で以下のコマンドを新しいセルにコピペして実行してください。これでMD計算がバックグラウンドで開始されます。

```bash
%%bash
# アップロードしたアーカイブを展開
tar -xzvf /content/drive/MyDrive/colab_transfer.tar.gz -C /content/

# 計算ディレクトリに移動
cd /content/SiC_3x3x10_MD

# Colab向けに用意した実行スクリプトをバックグラウンド実行
nohup bash run_colab.sh > nohup.out 2>&1 &

# ログをリアルタイムで表示
tail -f nohup.out
```

> [!TIP]
> `run_colab.sh` では、エラーでクラッシュした際も詳細なログが `qe_engine.log` や `nohup.out` に記録されるように修正されています。もし数ステップ動かした段階でエラーが出た場合は、このログの中身を確認してください。
