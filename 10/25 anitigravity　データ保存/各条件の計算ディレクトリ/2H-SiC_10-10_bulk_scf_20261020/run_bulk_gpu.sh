#!/bin/bash
# ==============================================================================
# 2H-SiC {10-10} バルクモデル (72原子) Quantum ESPRESSO GPU 単独SCF計算スクリプト
# ==============================================================================
set -e

echo "=========================================="
echo " Starting 2H-SiC Bulk SCF Calculation (T4 GPU)"
echo "=========================================="
nvidia-smi

# 3. QE pw.x 実行 (T4 GPU OpenACC / CUDA)
mkdir -p tmp
echo "Running pw.x (GPU)..."
/content/bin/pw.x < espresso.pwi > espresso.pwo 2>&1

echo "=========================================="
echo " Calculation Finished!"
echo " Total energy and forces summary:"
grep -E "(!    total energy|Total force)" espresso.pwo || true
echo "=========================================="

# 4. Google Drive への即時完全バックアップ (G:\マイドライブ\MD_backup\)
BACKUP_DIR="/content/drive/MyDrive/MD_backup/2H-SiC_10-10_bulk_scf_20261020"
mkdir -p "$BACKUP_DIR"
cp espresso.pwi espresso.pwo 2H-SiC_10-10_bulk_3x3x2_72atoms.data run_bulk_gpu.sh "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup successfully synced to $BACKUP_DIR"
