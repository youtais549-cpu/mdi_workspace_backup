#!/bin/bash
# ==============================================================================
# master_run_gpu.sh - Colab T4 GPU 実行 & Google Drive 自動同期スクリプト
# 保存先: G:\マイドライブ\MD_backup\真空層2.5Å\
# ==============================================================================
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

GDRIVE_DEST="/content/drive/MyDrive/MD_backup/真空層2.5Å"
mkdir -p "$GDRIVE_DEST"

echo "=== Master Relaxation Runner (Vacuum 2.5Å) ==="
echo "Local Directory: $DIR"
echo "Google Drive Backup: $GDRIVE_DEST"

# 5分間隔バックアップループ (バックグラウンド)
(
    while true; do
        sleep 300
        if [ -d "$DIR" ] && [ -d "$GDRIVE_DEST" ]; then
            cp -ru "$DIR"/* "$GDRIVE_DEST"/ 2>/dev/null || true
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Google Drive backup synced to $GDRIVE_DEST" >> backup.log
        fi
    done
) &
BACKUP_PID=$!

# 計算本体の実行
bash run_colab_gpu.sh

# 計算完了後の後処理
kill $BACKUP_PID 2>/dev/null || true

# 最終完全同期
echo "Performing final sync to Google Drive ($GDRIVE_DEST)..."
cp -ru "$DIR"/* "$GDRIVE_DEST"/ 2>/dev/null || true

echo "=== All Tasks Finished Successfully ==="
