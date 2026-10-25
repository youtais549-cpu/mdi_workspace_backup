#!/bin/bash

# 日付を取得 (YYYYMMDD形式)
TODAY=$(date +%Y%m%d)
FILE_NAME="conversation_logs_${TODAY}.txt"
WORKSPACE="/home/yamazaki/mdi_workspace_backup"
LOCAL_FILE="${WORKSPACE}/${FILE_NAME}"

# 1. ログを抽出してファイルを作成
python3 "${WORKSPACE}/extract_weekly_logs.py" "$LOCAL_FILE"

if [ ! -f "$LOCAL_FILE" ]; then
    echo "エラー: ログファイルの作成に失敗しました。"
    exit 1
fi

# 2. NASへアップロード (upload_to_nas.shを利用)
"${WORKSPACE}/upload_to_nas.sh" "$LOCAL_FILE"

# （必要に応じて）アップロード成功後にローカルファイルを削除する場合は以下のコメントを外します
# rm "$LOCAL_FILE"
