#!/bin/bash
# ==============================================================================
# run_bulk_scf_rtx5080.sh
# 【AGENTS.md §1 準拠: スラブ緩和前の「バルク 1 点 SCF 先行確定」プロトコル】
# 2H-SiC {10-10} バルク基準モデル (72原子, 真空 0 Å) の 1 点 SCF 計算を
# 新PC (Core Ultra 9 285K / RAM 64GB / RTX 5080 16GB) で実行・検証するスクリプト
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ローカル仮想環境があれば有効化
ENV_PREFIX="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
if [ -d "$ENV_PREFIX/bin" ]; then
    export PATH="$SCRIPT_DIR/bin:$ENV_PREFIX/bin:$PATH"
    export LD_LIBRARY_PATH="$ENV_PREFIX/lib:${LD_LIBRARY_PATH:-}"
elif [ -f "$HOME/.venvs/mdi_rtx5080/bin/activate" ]; then
    source "$HOME/.venvs/mdi_rtx5080/bin/activate"
fi

# OpenMPI & OpenMP 最適化 (Core Ultra 9 285K 24コア対応)
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_MAXSIZE=2147483648
NVHPC_ROOT=$(ls -d /opt/nvidia/hpc_sdk/Linux_x86_64/* 2>/dev/null | sort -V | tail -n 1 || true)
if [ -n "$NVHPC_ROOT" ]; then
    export PATH="$NVHPC_ROOT/compilers/bin:$NVHPC_ROOT/comm_libs/mpi/bin:$NVHPC_ROOT/cuda/bin:$PATH"
    export LD_LIBRARY_PATH="$NVHPC_ROOT/compilers/lib:$NVHPC_ROOT/math_libs/lib64:$NVHPC_ROOT/cuda/lib64:$NVHPC_ROOT/comm_libs/mpi/lib:$LD_LIBRARY_PATH"
fi

# pw.x バイナリの検出
PW_BIN=""
for cand in "$SCRIPT_DIR/bin/pw.x" "$HOME/.local/bin/pw.x" "$HOME/q-e-gpu/build/bin/pw.x" "/usr/local/bin/pw.x" "$(which pw.x 2>/dev/null || true)"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then
        PW_BIN="$cand"
        break
    fi
done

if [ -z "$PW_BIN" ]; then
    echo "❌ エラー: pw.x が見つかりません。先に 'bash setup_local_rtx5080_env.sh' を実行してください。"
    exit 1
fi

echo "============================================================"
echo " Starting 2H-SiC Bulk 1-Point SCF Verification (72 atoms)"
echo " Hardware: Core Ultra 9 285K / RAM 64GB / RTX 5080 16GB"
echo " Using pw.x: $PW_BIN"
echo "============================================================"
nvidia-smi --query-gpu=name,driver_version,memory.total,temperature.gpu,power.draw --format=csv

mkdir -p tmp
T0=$(date +%s)

if ldd "$PW_BIN" 2>/dev/null | grep -qE "libcuda|libcudart|libacc|libnvf"; then
    export OMP_NUM_THREADS=${QE_OMP_THREADS:-8}
    echo "[GPU Mode] Running: $PW_BIN -ndiag 1 < espresso_bulk_scf.pwi > espresso_bulk_scf.pwo"
    "$PW_BIN" -ndiag 1 < espresso_bulk_scf.pwi > espresso_bulk_scf.pwo 2>&1
else
    MPI_NP=${QE_MPI_NP:-8}
    export OMP_NUM_THREADS=${QE_OMP_THREADS:-2}
    echo "[MPI Mode] Running: mpirun -np $MPI_NP $PW_BIN -ndiag 1 < espresso_bulk_scf.pwi > espresso_bulk_scf.pwo"
    mpirun -np "$MPI_NP" "$PW_BIN" -ndiag 1 < espresso_bulk_scf.pwi > espresso_bulk_scf.pwo 2>&1
fi

T1=$(date +%s)
ELAPSED=$((T1 - T0))

echo "============================================================"
echo " Bulk SCF Finished in ${ELAPSED}s!"
grep -E "(!    total energy|Total force)" espresso_bulk_scf.pwo || true
echo "------------------------------------------------------------"
echo " [検証基準値 (T4 GPU 確定値)]"
echo "   E_bulk = -2347.1950 Ry = -31,935.3562 eV (-443.5466 eV/atom)"
echo "============================================================"

