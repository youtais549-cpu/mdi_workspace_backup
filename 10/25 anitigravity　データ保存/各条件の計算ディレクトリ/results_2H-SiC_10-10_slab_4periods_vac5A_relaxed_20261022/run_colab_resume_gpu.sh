#!/bin/bash
# ==============================================================================
# run_colab_resume_gpu.sh
# 途中再開用実行スクリプト (既存の dump.lammpstrj を削除せず追記・継続)
# ==============================================================================

echo "=========================================="
echo " Resuming LAMMPS + QE MDI Simulation (GPU)"
echo " Timestep 44 -> Final Relaxation"
echo "=========================================="

# 一時計算ディレクトリのみ再作成 (dump や既存ログは保護)
rm -rf tmp
mkdir -p tmp

# OpenMPI / 環境変数の最適化
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# 1. LAMMPS を MDI DRIVER としてバックグラウンド起動
echo "1. Starting LAMMPS MDI driver..."
/content/bin/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021" -in in.lammps > lmp.log 2>&1 &
LMP_PID=$!

sleep 1

# 2. Python QE MDI Engine (GPU) を起動
echo "2. Starting Python QE MDI engine (T4 GPU)..."
python3 qe_mdi_engine_core.py -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" > qe_engine.log 2>&1

# 3. 完了待機
wait $LMP_PID

echo "=========================================="
echo " Calculation Completed Successfully!"
echo " Converting trajectory to XYZ format..."
python3 make_xyz.py dump.lammpstrj md_animation.xyz 2>/dev/null || true
echo " Done!"
echo "=========================================="
