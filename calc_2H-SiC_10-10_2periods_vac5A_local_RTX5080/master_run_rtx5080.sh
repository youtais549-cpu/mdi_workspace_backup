#!/bin/bash
# ==============================================================================
# master_run_rtx5080.sh
# 2H-SiC {10-10} 2周期 (72原子) 真空層 5.0 Å 構造緩和計算 起動 & 自動バックアップスクリプト
# 対象PC: Intel Core Ultra 9 285K / RAM 64GB / NVIDIA GeForce RTX 5080 16GB / Windows 11 Pro
# ==============================================================================
set -e

WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORK_DIR"

# Google Drive (G:\マイドライブ\MD_backup\) がマウントされていればそこへ、なければローカルアーカイブへ保存
if [ -d "/mnt/g/マイドライブ/MD_backup" ]; then
    BACKUP_DIR="/mnt/g/マイドライブ/MD_backup/{101_0}2周期5Å_RTX5080検証"
else
    BACKUP_DIR="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/各条件の計算ディレクトリ/calc_2H-SiC_10-10_2periods_vac5A_local_RTX5080_backup"
fi
mkdir -p "$BACKUP_DIR"

echo "============================================================"
echo " 1. ハードウェア (RTX 5080 / Core Ultra 9 285K) 状態確認"
echo "============================================================"
nvidia-smi
lscpu | grep -E "Model name|CPU\(s\):" || true
free -h

echo "============================================================"
echo " 2. 初期ファイル（入力・構造・メタデータ・指示書）の退避"
echo "    保存先: $BACKUP_DIR"
echo "============================================================"
cp "$WORK_DIR"/in.lammps "$BACKUP_DIR/" 2>/dev/null || true
cp "$WORK_DIR"/*.data "$BACKUP_DIR/" 2>/dev/null || true
cp "$WORK_DIR"/fracture_metadata.json "$BACKUP_DIR/" 2>/dev/null || true
cp "$WORK_DIR"/RELAXATION_GRAPH_PROTOCOL.json "$BACKUP_DIR/" 2>/dev/null || true

# 5分間隔の自動同期ループ (AGENTS.md §1, §3)
nohup bash -c "while true; do
    cp \"$WORK_DIR\"/*.lammpstrj \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.xyz \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.log \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.pwo \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.pwi \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.png \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.pdf \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/*.svg \"$BACKUP_DIR/\" 2>/dev/null || true
    cp \"$WORK_DIR\"/nohup.out \"$BACKUP_DIR/\" 2>/dev/null || true
    sleep 300
done" > backup.log 2>&1 &
BACKUP_PID=$!

echo "============================================================"
echo " 3. 計算のバックグラウンド開始 (PID 管理付き)"
echo "============================================================"
nohup bash run_slab_rtx5080.sh > nohup.out 2>&1 &
CALC_PID=$!

echo "🚀 RTX 5080 新環境での 2周期 (72原子) 真空層 5.0 Å 構造緩和計算を開始しました！"
echo "  - 計算プロセス PID       : $CALC_PID"
echo "  - 自動バックアップ PID   : $BACKUP_PID"
echo "  - 全体進捗モニター       : tail -f $WORK_DIR/nohup.out"
echo "  - QE エンジン詳細ログ    : tail -f $WORK_DIR/qe_engine.log"
echo "  - LAMMPS 構造緩和ログ    : tail -f $WORK_DIR/lmp.log"

