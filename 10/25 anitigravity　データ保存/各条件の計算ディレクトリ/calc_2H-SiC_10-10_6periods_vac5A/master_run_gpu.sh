#!/bin/bash
# ==============================================================================
# master_run_gpu.sh
# 2H-SiC {10-10} 6周期 (12層, 216原子) 真空層 5.0 Å 構造緩和計算実行スクリプト
# バックアップ先: G:\マイドライブ\MD_backup\[101_0]6周期５Å\
# ==============================================================================

echo "1. Python パッケージの確認..."
pip install --quiet ase pymdi

echo "2. バイナリの配置と確認..."
mkdir -p /content/bin
if [ -f /content/drive/MyDrive/mdi_binaries/lmp ]; then
    cp /content/drive/MyDrive/mdi_binaries/lmp /content/bin/
fi
if [ -f /content/drive/MyDrive/mdi_binaries/pw.x.real ]; then
    cp /content/drive/MyDrive/mdi_binaries/pw.x.real /content/bin/
fi
if [ -f /content/drive/MyDrive/mdi_binaries/pw.x ]; then
    cp /content/drive/MyDrive/mdi_binaries/pw.x /content/bin/
fi
chmod +x /content/bin/* 2>/dev/null || true

echo "3. GPU 稼働状態の確認..."
nvidia-smi

echo "4. 自動バックアップの設定 (5分間隔 -> /content/drive/MyDrive/MD_backup/[101_0]6周期５Å)..."
WORK_DIR=$(pwd)
BACKUP_DIR="/content/drive/MyDrive/MD_backup/[101_0]6周期５Å"
mkdir -p "$BACKUP_DIR"

# 初期ファイル（入力・構造・メタデータ）を即時バックアップ
cp "$WORK_DIR"/in.lammps "$BACKUP_DIR/" 2>/dev/null || true
cp "$WORK_DIR"/in.lammps.optimized_conv "$BACKUP_DIR/" 2>/dev/null || true
cp "$WORK_DIR"/*.data "$BACKUP_DIR/" 2>/dev/null || true
cp "$WORK_DIR"/fracture_metadata.json "$BACKUP_DIR/" 2>/dev/null || true

# 5分間隔の自動同期ループ
nohup bash -c "while true; do 
    cp $WORK_DIR/*.lammpstrj \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.xyz \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.log \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.pwo \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.pwi \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/nohup.out \"$BACKUP_DIR/\" 2>/dev/null || true
    sleep 300
done" > backup.log 2>&1 &

echo "5. 計算のバックグラウンド開始..."
nohup bash run_colab_gpu.sh > nohup.out 2>&1 &

echo "🚀 6周期 (12層, 216原子) T4 GPU による計算がスタートしました！"
echo "ログ確認コマンド: tail -f nohup.out"
