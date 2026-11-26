#!/bin/bash
# ==============================================================================
# setup_local_rtx5080_env.sh
# 新PC (Core Ultra 9 285K / RAM 64GB / RTX 5080 16GB / Windows 11 Pro WSL2) 用
# root権限 (sudo) 不要の高速セットアップスクリプト
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
ENV_PREFIX="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
MAMBA_ROOT="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/micromamba"
MAMBA_BIN="$MAMBA_ROOT/bin/micromamba"
LOCAL_BIN="$SCRIPT_DIR/bin"
mkdir -p "$MAMBA_ROOT/bin" "$LOCAL_BIN"

echo "============================================================"
echo " Step 1: Micromamba パッケージマネージャの確認 (sudo 不要)"
echo "============================================================"
if [ ! -x "$MAMBA_BIN" ]; then
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj -C "$MAMBA_ROOT/bin" --strip-components=1 bin/micromamba
    chmod +x "$MAMBA_BIN"
fi
echo "✅ Micromamba ready: $MAMBA_BIN"

echo "============================================================"
echo " Step 2: Quantum ESPRESSO (pw.x) & Python 3.11 & CMake の高速導入"
echo "============================================================"
if [ ! -x "$ENV_PREFIX/bin/pw.x" ]; then
    rm -rf "$ENV_PREFIX"
    "$MAMBA_BIN" create -y -p "$ENV_PREFIX" -c conda-forge \
        python=3.11 pip cmake qe
else
    echo "✅ Quantum ESPRESSO ($ENV_PREFIX/bin/pw.x) already installed."
fi

export PATH="$LOCAL_BIN:$ENV_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$ENV_PREFIX/lib:${LD_LIBRARY_PATH:-}"

echo "============================================================"
echo " Step 3: Python パッケージ (NumPy, SciPy, Matplotlib, ASE, PyMDI) の導入"
echo "============================================================"
"$ENV_PREFIX/bin/pip" install --quiet numpy scipy matplotlib ase pymdi
echo "✅ Python packages (ase, pymdi, numpy, scipy, matplotlib) installed."

echo "============================================================"
echo " Step 4: 論文・Word グラフ用フォント (MS明朝 / Times New Roman) 配置"
echo "============================================================"
for f in "$WORKSPACE_DIR/msmincho.ttc" "$WORKSPACE_DIR/times.ttf" "$WORKSPACE_DIR/環境設定・フォント/msmincho.ttc" "$WORKSPACE_DIR/環境設定・フォント/times.ttf"; do
    if [ -f "$f" ]; then
        cp "$f" "$SCRIPT_DIR/" 2>/dev/null || true
    fi
done
echo "✅ Fonts copied to calculation directory."

echo "============================================================"
echo " Step 5: LAMMPS (PKG_MDI=ON) の 24スレッド高速ビルド (Core Ultra 9 285K)"
echo "============================================================"
if [ ! -x "$LOCAL_BIN/lmp" ]; then
    BUILD_ROOT="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/lammps_mdi_build"
    mkdir -p "$BUILD_ROOT"
    if [ ! -d "$BUILD_ROOT/lammps" ]; then
        git clone --depth 1 -b release https://github.com/lammps/lammps.git "$BUILD_ROOT/lammps"
    fi
    rm -rf "$BUILD_ROOT/lammps/build"
    mkdir -p "$BUILD_ROOT/lammps/build"
    cd "$BUILD_ROOT/lammps/build"
    "$ENV_PREFIX/bin/cmake" ../cmake \
        -DCMAKE_C_COMPILER=/usr/bin/gcc \
        -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_MPI=OFF \
        -DBUILD_OMP=ON \
        -DPKG_MDI=ON \
        -DPKG_MANYBODY=ON
    "$ENV_PREFIX/bin/cmake" --build . -j 24
    cp lmp "$LOCAL_BIN/lmp"
    cp lmp "$ENV_PREFIX/bin/lmp"
    echo "✅ LAMMPS (PKG_MDI=ON) built and installed to $LOCAL_BIN/lmp"
else
    echo "✅ LAMMPS ($LOCAL_BIN/lmp) already built."
fi

ln -sf "$ENV_PREFIX/bin/pw.x" "$LOCAL_BIN/pw.x"

echo "============================================================"
echo " 🎉 セットアップ完了！"
echo "  - Python : $(which python3)"
echo "  - pw.x   : $(which pw.x)"
echo "  - lmp    : $(which lmp)"
echo "============================================================"
