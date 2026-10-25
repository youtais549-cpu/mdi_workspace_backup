#!/bin/bash
# ==============================================================================
# resume_run_gpu.sh
# 2H-SiC {10-10} 4周期 (8層, 144原子) 真空層 5.0 Å 構造緩和計算【再開用スクリプト】
# 前回の途中緩和構造 (Timestep 44) から同一条件でシームレスに再開します。
# ==============================================================================

WORK_DIR=$(pwd)
BACKUP_DIR="/content/drive/MyDrive/MD_backup/[101_0]4周期５Å"
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo " Resuming 4-period 2H-SiC Slab Relaxation"
echo " Initial Structure: slab_10-10_144atoms_restart.data (Timestep 44)"
echo "=========================================="

# 1. 既存の残存プロセスを念のためクリーンアップ
killall -9 pw.x.real pw.x lmp 2>/dev/null || true
pkill -f qe_mdi_engine 2>/dev/null || true
sleep 1

# 2. in.lammps を再開用設定に切り替え
cp in.lammps.restart in.lammps

# 3. 自動バックアップループの開始 (5分間隔)
nohup bash -c "while true; do 
    cp $WORK_DIR/*.lammpstrj \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.xyz \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.log \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.pwo \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/*.pwi \"$BACKUP_DIR/\" 2>/dev/null || true
    cp $WORK_DIR/nohup.out \"$BACKUP_DIR/\" 2>/dev/null || true
    sleep 300
done" > backup.log 2>&1 &

# 4. 計算のバックグラウンド開始
nohup bash run_colab_gpu.sh > nohup.out 2>&1 &

echo "🚀 計算が再開されました！"
echo "ログ確認コマンド: tail -f nohup.out"
