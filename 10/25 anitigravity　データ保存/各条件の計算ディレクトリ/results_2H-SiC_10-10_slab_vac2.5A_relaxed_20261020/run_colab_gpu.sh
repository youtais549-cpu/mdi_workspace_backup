#!/bin/bash
# ==============================================================================
# run_colab_gpu.sh - Colab T4 GPU 用 MDI 起動スクリプト (真空層 2.5Å スラブ)
# ==============================================================================
set -e
PORT=8026
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [MDI Launcher] 2H-SiC {10-10} Slab (Vacuum 2.5Å) GPU Relaxation ==="
echo "Working directory: $DIR"
echo "MDI Port: $PORT"

# 既存プロセスの安全停止
pkill -f qe_mdi_engine_gpu.py || true
killall -9 pw.x lmp pw.x.real 2>/dev/null || true
sleep 1

# 1. LAMMPS Driver 起動
echo "[1/2] Starting LAMMPS driver..."
/content/bin/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port ${PORT}" -in in.lammps > log.lammps 2>&1 &
PID_LMP=$!

sleep 2

# 2. QE MDI Engine (GPU) 起動
echo "[2/2] Starting QE MDI Engine (GPU)..."
python3 qe_mdi_engine_gpu.py -mdi "-role ENGINE -name QE -method TCP -port ${PORT} -hostname localhost" > qe_engine.log 2>&1 &
PID_QE=$!

echo "Processes started: LAMMPS (PID: $PID_LMP), QE Engine (PID: $PID_QE)"
echo "Waiting for relaxation to complete..."

# LAMMPS 終了待機
wait $PID_LMP
echo "LAMMPS driver finished. Waiting for QE engine to finalize..."
wait $PID_QE 2>/dev/null || true

# Winmostar 用 XYZ アニメーション生成
if [ -f "dump.lammpstrj" ]; then
    echo "Generating Winmostar animation XYZ..."
    python3 make_xyz.py dump.lammpstrj md_animation.xyz || true
fi

echo "=== MDI Relaxation Completed Successfully ==="
