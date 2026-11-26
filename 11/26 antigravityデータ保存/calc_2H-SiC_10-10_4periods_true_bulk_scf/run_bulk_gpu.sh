#!/bin/bash
set -e
echo "=========================================="
echo " Starting True 144-atoms Bulk SCF Calculation (T4 GPU)"
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
