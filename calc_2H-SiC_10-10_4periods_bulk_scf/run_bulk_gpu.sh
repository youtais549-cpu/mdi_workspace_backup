#!/bin/bash
# ==============================================================================
# 2H-SiC {10-10} 4周期バルクモデル (144原子) Quantum ESPRESSO GPU 単独SCF計算スクリプト
# ==============================================================================
set -e

echo "=========================================="
echo " Starting 2H-SiC 4-periods Bulk SCF Calculation (T4 GPU)"
echo "=========================================="
nvidia-smi

mkdir -p tmp
echo "Running pw.x (GPU)..."
/content/bin/pw.x < espresso.pwi > espresso.pwo 2>&1

echo "=========================================="
echo " Bulk Calculation Finished!"
echo " Total energy and forces summary:"
grep -E "(!    total energy|Total force)" espresso.pwo || true
echo "=========================================="
