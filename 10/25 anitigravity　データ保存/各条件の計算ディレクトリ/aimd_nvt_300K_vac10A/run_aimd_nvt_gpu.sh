#!/bin/bash
# ==============================================================================
# run_aimd_nvt_gpu.sh
# 2H-SiC {10-10} 72原子スラブ (真空層各10Å)
# 300K NVT 第一原理分子動力学 (AIMD) MDI 起動スクリプト (Colab T4 GPU 用)
# ==============================================================================

set -e
PORT=8025
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "========================================================================"
echo "  2H-SiC {10-10} 300K NVT AIMD (LAMMPS + Quantum ESPRESSO GPU via MDI)"
echo "========================================================================"
echo "Workdir: $DIR"
echo "Port:    $PORT"

# 既存プロセスの安全停止
pkill -f qe_mdi_engine_gpu.py || true
killall -9 pw.x lmp pw.x.real 2>/dev/null || true
sleep 1

# 1. LAMMPS (Driver) 起動
echo "[1/3] Starting LAMMPS driver (NVT @ 300K)..."
/content/bin/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port ${PORT}" -in in.lammps > log.lammps 2>&1 &
PID_LMP=$!

sleep 2

# 2. QE MDI Engine (GPU) 起動
echo "[2/3] Starting QE MDI GPU Engine..."
python3 qe_mdi_engine_gpu.py -mdi "-role ENGINE -name QE -method TCP -port ${PORT} -hostname localhost" > qe_engine.log 2>&1 &
PID_QE=$!

echo "Processes started: LAMMPS (PID: $PID_LMP), QE Engine (PID: $PID_QE)"
echo "Waiting for AIMD simulation to complete..."

# 終了待機
wait $PID_LMP
echo "[3/3] LAMMPS completed. Waiting for QE engine to finalize..."
wait $PID_QE 2>/dev/null || true

# Winmostar 用 XYZ アニメーション生成
if [ -f "dump.lammpstrj" ]; then
    echo "Converting dump.lammpstrj to Winmostar animation XYZ..."
    python3 make_xyz.py dump.lammpstrj md_nvt_animation.xyz || true
fi

echo "========================================================================"
echo "  300K NVT AIMD Simulation Completed Successfully!"
echo "========================================================================"
