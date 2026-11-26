#!/bin/bash
# ==============================================================================
# sync_live_espresso.sh
# Colab 上で実行中の 6周期スラブ緩和計算の espresso.pwo を
# ローカルの live_espresso.pwo へリアルタイム（3秒間隔）で同期するスクリプト
# ==============================================================================

REMOTE_PATH="/content/calc_2H-SiC_10-10_2periods_vac2.5A_2nd/espresso.pwo"
LOCAL_PATH="/home/yamazaki/mdi_workspace_backup/live_espresso.pwo"

echo "🔄 Colab から live_espresso.pwo へのリアルタイム同期を開始しました（3秒間隔）"
echo "停止するには [Ctrl + C] を押してください。"

while true; do
    scp -q colab:"$REMOTE_PATH" "$LOCAL_PATH" 2>/dev/null || true
    sleep 3
done
