#!/bin/bash

# NAS アップロードスクリプト
# 使い方: ./upload_to_nas.sh <アップロードしたいファイルのパス>

if [ -z "$1" ]; then
    echo "エラー: アップロードするファイルを指定してください。"
    echo "使い方: $0 <ファイルパス>"
    exit 1
fi

LOCAL_FILE="$1"

if [ ! -f "$LOCAL_FILE" ]; then
    echo "エラー: ファイル '$LOCAL_FILE' が見つかりません。"
    exit 1
fi

FILE_NAME=$(basename "$LOCAL_FILE")
NAS_SHARE="//192.168.12.69/Backup"
REMOTE_DIR="Yamazaki-tj\\新しいフォルダー (2)"
CRED_FILE="$HOME/.smbcredentials"

if [ ! -f "$CRED_FILE" ]; then
    echo "エラー: 認証ファイル ($CRED_FILE) が見つかりません。"
    exit 1
fi

echo "======================================"
echo "NASへアップロードを開始します..."
echo "ファイル: $FILE_NAME"
echo "送信先: $NAS_SHARE/$REMOTE_DIR"
echo "======================================"

# smbclientを使ってファイルをアップロード
smbclient "$NAS_SHARE" -A "$CRED_FILE" -c "cd \"$REMOTE_DIR\"; put \"$LOCAL_FILE\" \"$FILE_NAME\""

if [ $? -eq 0 ]; then
    echo "======================================"
    echo "アップロード成功！"
    echo "======================================"
else
    echo "======================================"
    echo "エラー: アップロードに失敗しました。"
    echo "======================================"
fi
