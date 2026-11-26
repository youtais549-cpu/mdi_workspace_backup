#!/bin/bash
# master_run.sh
# Colabの環境構築とMD計算の実行、自動バックアップを行うマスタースクリプト

echo "1. 必要なライブラリとNVHPCのインストール..."
pip install ase pymdi
# NVHPCのインストール (GPU用ライブラリ)
echo "deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /" | sudo tee /etc/apt/sources.list.d/nvhpc.list
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nvhpc-24-7

echo "2. バイナリと作業ディレクトリのセットアップ..."
mkdir -p /content/bin
cp /content/drive/MyDrive/mdi_binaries/lmp /content/bin/
chmod +x /content/bin/*

mkdir -p /content/SiC_3x3x10_MD
# Google Driveから最新のスクリプトとデータを一式コピー (削除: スクリプトを上書きしてしまうため)
# cp -r /content/drive/MyDrive/SiC_MD_backup/* /content/SiC_3x3x10_MD/ 2>/dev/null || true

echo "3. 計算の開始（バックグラウンド実行）..."
cd /content/SiC_3x3x10_MD
nohup bash run_colab.sh > nohup.out 2>&1 &

echo "4. 自動バックアップの設定（5分間隔）..."
# nohup.out も含めてバックアップするように修正
nohup bash -c 'while true; do cp /content/SiC_3x3x10_MD/*.lammpstrj /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/*.pwo /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/qe_engine.log /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/nohup.out /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; sleep 300; done' > backup_nohup.out 2>&1 &

echo "🚀 すべての準備が完了し、計算がスタートしました！"
echo "進行状況のログは自動的にGoogle Driveへ同期されます。"
