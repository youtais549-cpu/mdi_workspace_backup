#!/bin/bash
ssh colab << 'SSH_EOF'
cd /content/q-e
mkdir -p build_gpu_serial
cd build_gpu_serial
export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/23.11
export PATH=$NVHPC_HOME/compilers/bin:$NVHPC_HOME/cuda/bin:$PATH
export LD_LIBRARY_PATH=$NVHPC_HOME/compilers/lib:$NVHPC_HOME/math_libs/lib64:$NVHPC_HOME/cuda/lib64:/usr/local/cuda/lib64:/usr/lib64-nvidia:$LD_LIBRARY_PATH
cmake .. -DCMAKE_C_COMPILER=nvc -DCMAKE_Fortran_COMPILER=nvfortran -DQE_ENABLE_MPI=OFF -DQE_ENABLE_OPENACC=ON -DQE_ENABLE_CUDA=ON -DNVFORTRAN_CUDA_CC=75 -DQE_FFTW_VENDOR=Internal
make pw -j4
cp bin/pw.x /content/bin/pw.x.serial
SSH_EOF
