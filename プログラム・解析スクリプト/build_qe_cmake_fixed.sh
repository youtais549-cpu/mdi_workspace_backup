#!/bin/bash
# GPU用 Quantum ESPRESSO (v7.3) のCMakeビルドスクリプト
# NVHPC 24.7 (Colab最新) に合わせて設定

cd /content

echo "=== NVIDIA HPC SDK (24.7) 環境設定 ==="
# /usr/lib64-nvidia is crucial for detecting CUDA drivers in Colab SSH!
export LD_LIBRARY_PATH=/usr/lib64-nvidia:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/cuda/12.2/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi/lib:$LD_LIBRARY_PATH
export PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi/bin:$PATH

echo "=== Quantum ESPRESSO ソースのクローン ==="
rm -rf q-e
git clone -b qe-7.3 --depth 1 https://gitlab.com/QEF/q-e.git
cd q-e
mkdir build
cd build

echo "=== CMake 設定 (GPU, MDI無効, MPI有効) ==="
cmake \
  -DCMAKE_C_COMPILER=nvc \
  -DCMAKE_Fortran_COMPILER=nvfortran \
  -DQE_ENABLE_CUDA=ON \
  -DNVFORTRAN_CUDA_CC=75 \
  -DQE_ENABLE_MPI=ON \
  -DQE_ENABLE_MDI=ON \
  -DQE_FFTW_VENDOR=Internal \
  -DCMAKE_INSTALL_PREFIX=/content \
  ..

echo "=== ビルド開始 ==="
make -j4 pw

echo "=== インストール ==="
make install

echo "=== /content/bin にコピー ==="
mkdir -p /content/bin
cp bin/pw.x /content/bin/
