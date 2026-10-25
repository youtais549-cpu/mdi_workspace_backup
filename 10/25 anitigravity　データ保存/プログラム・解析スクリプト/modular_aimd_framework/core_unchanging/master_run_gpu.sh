#!/bin/bash
# ==============================================================================
# master_run_gpu.sh
# Colab上でT4 GPU環境をセットアップし、MDI計算を実行・バックアップするスクリプト
# 【固定コアコード: ユーザー編集不要】
# ==============================================================================

echo "1. Python パッケージの確認とインストール..."
pip install --quiet ase pymdi

echo "2. NVIDIA HPC SDK (NVHPC) の確認..."
if [ ! -d /opt/nvidia/hpc_sdk ]; then
    echo "NVHPC SDK をインストールしています (GPU用ライブラリ)..."
    echo "deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /" | sudo tee /etc/apt/sources.list.d/nvhpc.list
    sudo apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nvhpc-24-7
else
    echo "NVHPC SDK はすでにインストールされています。"
fi

echo "3. バイナリの配置と確認..."
mkdir -p /content/bin
mkdir -p /content/drive/MyDrive/mdi_binaries

# Google Drive から既存バイナリの同期
if [ -f /content/drive/MyDrive/mdi_binaries/lmp ]; then
    cp /content/drive/MyDrive/mdi_binaries/lmp /content/bin/
fi
if [ -f /content/drive/MyDrive/mdi_binaries/pw.x.real ]; then
    cp /content/drive/MyDrive/mdi_binaries/pw.x.real /content/bin/
fi
if [ -f /content/drive/MyDrive/mdi_binaries/pw.x ]; then
    cp /content/drive/MyDrive/mdi_binaries/pw.x /content/bin/
fi

# LAMMPS (MDI対応) の自動ビルド (未ビルド時のみ実行)
if [ ! -x /content/bin/lmp ]; then
    echo "LAMMPS (MDI対応) をビルドしています..."
    cd /content
    if [ ! -d /content/lammps ]; then
        git clone -b stable_2Aug2023_update3 https://github.com/lammps/lammps.git
    fi
    mkdir -p /content/lammps/build && cd /content/lammps/build
    cmake ../cmake -D PKG_MDI=yes -D MDI_USE_PYTHON_PLUGINS=OFF
    make -j$(nproc)
    cp lmp /content/bin/
    cp lmp /content/drive/MyDrive/mdi_binaries/
    echo "✅ LAMMPS ビルド完了！"
fi

# Quantum ESPRESSO (T4 GPU対応) の自動ビルド (未ビルド時のみ実行)
if [ ! -x /content/bin/pw.x.real ]; then
    echo "Quantum ESPRESSO (T4 GPU対応) をビルドしています..."
    export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7
    rm -f $NVHPC_HOME/cuda/12.2 2>/dev/null || true
    ln -sf 12.5 $NVHPC_HOME/cuda/12.2
    export PATH=$NVHPC_HOME/compilers/bin:$NVHPC_HOME/comm_libs/mpi/bin:$NVHPC_HOME/cuda/bin:$PATH
    export LD_LIBRARY_PATH=$NVHPC_HOME/compilers/lib:$NVHPC_HOME/comm_libs/mpi/lib:$NVHPC_HOME/cuda/lib64:$LD_LIBRARY_PATH
    export CUDA_HOME=$NVHPC_HOME/cuda

    cd /content
    if [ ! -d /content/q-e ]; then
        git clone -b qe-7.2 https://gitlab.com/QEF/q-e.git
    fi
    cd /content/q-e
    ./configure CC=nvc FC=nvfortran F90=nvfortran MPIF90=mpif90 --with-cuda=$CUDA_HOME --with-cuda-runtime=12.5 --with-cuda-cc=75 BLAS_LIBS="-lblas" LAPACK_LIBS="-llapack"
    make pw -j$(nproc)
    cp bin/pw.x /content/bin/pw.x.real
    cp bin/pw.x /content/drive/MyDrive/mdi_binaries/pw.x.real
    
    cat << 'WRAPPER_EOF' > /content/bin/pw.x
#!/bin/bash
HPCX_INIT=$(find /opt/nvidia/hpc_sdk/Linux_x86_64 -name "hpcx-init.sh" 2>/dev/null | sort -V | tail -n 1)
if [ -n "$HPCX_INIT" ] && [ -f "$HPCX_INIT" ]; then
    source "$HPCX_INIT"
    hpcx_load
fi
exec mpirun --allow-run-as-root -np 1 /content/bin/pw.x.real "$@"
WRAPPER_EOF
    chmod +x /content/bin/pw.x /content/bin/pw.x.real
    cp /content/bin/pw.x /content/drive/MyDrive/mdi_binaries/pw.x
    echo "✅ Quantum ESPRESSO ビルド完了！"
fi

chmod +x /content/bin/* 2>/dev/null || true

echo "4. GPU 稼働状態の確認..."
nvidia-smi

echo "5. 計算のバックグラウンド開始..."
WORK_DIR=$(pwd)
nohup bash run_colab_gpu.sh > nohup.out 2>&1 &

echo "6. 自動バックアップの設定 (5分間隔 -> G:\\マイドライブ\\MD_backup)..."
BACKUP_DIR="/content/drive/MyDrive/MD_backup"
mkdir -p "$BACKUP_DIR"
nohup bash -c "while true; do 
    cp $WORK_DIR/*.lammpstrj $BACKUP_DIR/ 2>/dev/null || true
    cp $WORK_DIR/*.xyz $BACKUP_DIR/ 2>/dev/null || true
    cp $WORK_DIR/*.log $BACKUP_DIR/ 2>/dev/null || true
    cp $WORK_DIR/*.pwo $BACKUP_DIR/ 2>/dev/null || true
    cp $WORK_DIR/*.pwi $BACKUP_DIR/ 2>/dev/null || true
    cp $WORK_DIR/nohup.out $BACKUP_DIR/ 2>/dev/null || true
    sleep 300
done" > backup.log 2>&1 &

echo "🚀 T4 GPU による計算がスタートしました！"
echo "ログ確認コマンド: tail -f nohup.out"
