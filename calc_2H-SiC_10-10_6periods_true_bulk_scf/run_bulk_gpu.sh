#!/bin/bash
set -e
# ==============================================================================
# run_bulk_gpu.sh
# 2H-SiC {10-10} 6周期 (216原子) 真のバルクモデル QE GPU 1点SCF計算実行スクリプト
# バックアップ先: G:\マイドライブ\MD_backup\{101_0}6周期5Å　2回目(収束条件変更後)\
# ==============================================================================

echo "=========================================="
echo " Starting True 216-atoms Bulk SCF Calculation (T4 GPU)"
echo "=========================================="
nvidia-smi

mkdir -p tmp
echo "Running pw.x (GPU)..."
/content/bin/pw.x < espresso.pwi > espresso.pwo 2>&1

echo "=========================================="
echo " True Bulk Calculation Finished!"
echo " Total energy and forces summary:"
grep -E "(!    total energy|Total force)" espresso.pwo || true
echo "=========================================="

# Google Drive への自動保存
BACKUP_DIR="/content/drive/MyDrive/MD_backup/{101_0}6周期5Å　2回目(収束条件変更後)"
mkdir -p "$BACKUP_DIR/bulk"
cp -r * "$BACKUP_DIR/bulk/" 2>/dev/null || true
cp espresso.pwo "$BACKUP_DIR/bulk_espresso.pwo" 2>/dev/null || true
cp bulk_10-10_216atoms_true_bulk.data "$BACKUP_DIR/" 2>/dev/null || true
echo "Saved bulk calculation results to $BACKUP_DIR"
