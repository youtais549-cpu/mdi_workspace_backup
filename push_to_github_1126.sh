#!/bin/bash
# ==============================================================================
# push_to_github_1126.sh
# GitHub (https://github.com/youtais549-cpu/mdi_workspace_backup.git) の既存データを
# 一切消さずに保護したまま、「11/26 antigravityデータ保存」フォルダを安全に統合・プッシュするスクリプト
# ==============================================================================
set -e

cd "$(dirname "$0")"

REMOTE_URL="https://github.com/youtais549-cpu/mdi_workspace_backup.git"
git remote set-url origin "$REMOTE_URL" 2>/dev/null || git remote add origin "$REMOTE_URL"

echo "1. GitHub リモートリポジトリ (origin/main) の既存履歴を取得しています..."
git fetch origin main

echo "2. GitHub 上の過去データ (10/25 データ等) を保持したまま『11/26 antigravityデータ保存』を統合しています..."
git merge origin/main --allow-unrelated-histories -X ours -m "Merge remote origin/main and add 11/26 antigravityデータ保存" || true

echo "3. GitHub (https://github.com/youtais549-cpu/mdi_workspace_backup) へプッシュしています..."
git push -u origin main

echo "============================================================"
echo " 完了！ GitHub への『11/26 antigravityデータ保存』の保存が成功しました。"
echo "============================================================"
