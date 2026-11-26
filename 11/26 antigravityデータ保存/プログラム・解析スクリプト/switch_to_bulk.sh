#!/bin/bash
# ==============================================================================
# switch_to_bulk.sh
# 6周期 (216原子) の現在進行中ステップ (Step 39) の完了を監視し、
# 完了直後に安全停止 -> Driveバックアップ -> 144原子バルクSCF計算を開始する自動連携スクリプト
# ==============================================================================
set -e

WORK_DIR="/content/SiC_6periods_vac5A_MD_restart"
BULK_DIR="/content/SiC_4periods_bulk_scf"
BACKUP_6P="/content/drive/MyDrive/MD_backup/[101_0]6周期５Å(境界条件変更)/restart"

echo "=== 1. 現在のステップ (Step 39) の力計算完了を監視中... ==="
# espresso.pwo に "Forces acting on atoms" が現れるのを待つ
# 既に過去ステップの Forces acting on atoms がある可能性を考慮し、現在の行数を取得
INITIAL_LINES=$(wc -l < "$WORK_DIR/espresso.pwo" 2>/dev/null || echo 0)
echo "監視開始時の espresso.pwo 行数: $INITIAL_LINES"

while true; do
    # 現在の行数が INITIAL_LINES より後の部分に "Forces acting on atoms" が出現したか判定
    if tail -n +$INITIAL_LINES "$WORK_DIR/espresso.pwo" | grep -q "Forces acting on atoms"; then
        echo "🎉 Step 39 の SCF 収束および力計算の完了を検知しました！"
        break
    fi
    # 万一プロセスが終了している場合の安全策
    if ! pgrep -f "pw.x.real" > /dev/null && ! pgrep -f "lmp" > /dev/null; then
        echo "⚠️ プロセスが既に終了しています。"
        break
    fi
    sleep 5
done

# LAMMPS が dump.lammpstrj を書き込む時間を確保
echo "LAMMPS のダンプファイル書き込み完了を待機中 (10秒)..."
sleep 10

echo "=== 2. 6周期計算の安全一時停止 ==="
# ルール3に従い、Colabカーネルを殺さないよう pw.x.real, lmp, qe_mdi_engine のみを停止
killall -9 pw.x.real pw.x lmp 2>/dev/null || true
pkill -f qe_mdi_engine 2>/dev/null || true
sleep 3

# GPU メモリ解放の確認
echo "GPU メモリ状態:"
nvidia-smi

echo "=== 3. 6周期成果物の Google Drive への完全バックアップ ==="
mkdir -p "$BACKUP_6P"
cp "$WORK_DIR"/*.lammpstrj "$BACKUP_6P/" 2>/dev/null || true
cp "$WORK_DIR"/*.pwo "$BACKUP_6P/" 2>/dev/null || true
cp "$WORK_DIR"/*.log "$BACKUP_6P/" 2>/dev/null || true
cp "$WORK_DIR"/*.xyz "$BACKUP_6P/" 2>/dev/null || true
echo "✅ 6周期の最新成果物を Google Drive に同期しました。"

echo "=== 4. 144原子 (4周期) バルクモデルの QE GPU SCF 計算の開始 ==="
cd "$BULK_DIR"
bash run_bulk_gpu.sh

echo "🎉 144原子 バルク計算が完了しました！"
