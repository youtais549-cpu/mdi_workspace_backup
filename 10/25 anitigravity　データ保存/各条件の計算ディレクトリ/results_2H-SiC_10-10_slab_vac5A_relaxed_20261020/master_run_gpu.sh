#!/bin/bash
# ==============================================================================
# master_run_gpu.sh
# 2H-SiC {10-10} スラブモデル (真空層 5.0Å, 72原子)
# T4 GPU 構造緩和計算 起動 & Google Drive 自動同期スクリプト
# ==============================================================================

WORK_DIR="/content/2H-SiC_10-10_slab_vac5A_relaxed_20261020"
BACKUP_DIR="/content/drive/MyDrive/MD_backup/2H-SiC_10-10_slab_vac5A_relaxed_20261020"

echo "1. Python パッケージの確認..."
pip install --quiet ase pymdi

echo "2. NVHPC 環境の確認..."
NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7
if [ ! -d "$NVHPC_HOME" ]; then
    echo "NVHPC SDK をインストールしています..."
    echo "deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /" | sudo tee /etc/apt/sources.list.d/nvhpc.list
    sudo apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nvhpc-24-7
fi

echo "3. バイナリの配置..."
mkdir -p /content/bin
if [ -f /content/drive/MyDrive/mdi_binaries/lmp ]; then
    cp /content/drive/MyDrive/mdi_binaries/lmp /content/bin/
fi
if [ -f /content/drive/MyDrive/mdi_binaries/pw.x.real ]; then
    cp /content/drive/MyDrive/mdi_binaries/pw.x.real /content/bin/
fi

# pw.x ラッパー
cat << 'WRAPPER_EOF' > /content/bin/pw.x
#!/bin/bash
NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7
rm -f $NVHPC_HOME/cuda/12.2 2>/dev/null || true
ln -sf 12.5 $NVHPC_HOME/cuda/12.2 2>/dev/null || true
export PATH=$NVHPC_HOME/compilers/bin:$NVHPC_HOME/comm_libs/mpi/bin:$NVHPC_HOME/cuda/bin:$PATH
export LD_LIBRARY_PATH=$NVHPC_HOME/compilers/lib:$NVHPC_HOME/math_libs/lib64:$NVHPC_HOME/cuda/lib64:$NVHPC_HOME/comm_libs/mpi/lib:$LD_LIBRARY_PATH
HPCX_INIT=$(find /opt/nvidia/hpc_sdk/Linux_x86_64 -name "hpcx-init.sh" 2>/dev/null | sort -V | tail -n 1)
if [ -n "$HPCX_INIT" ] && [ -f "$HPCX_INIT" ]; then
    source "$HPCX_INIT"
    hpcx_load
fi
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
exec mpirun --allow-run-as-root -np 1 /content/bin/pw.x.real "$@"
WRAPPER_EOF

chmod +x /content/bin/* 2>/dev/null || true

echo "4. GPU 状態の確認..."
nvidia-smi

echo "5. 計算のバックグラウンド開始..."
cd "$WORK_DIR"
nohup bash run_colab_gpu.sh > nohup.out 2>&1 &
CALC_PID=$!

echo "6. Google Drive への自動バックアップ設定 (5分間隔)..."
mkdir -p "$BACKUP_DIR"
nohup bash -c '
WORK_DIR="/content/2H-SiC_10-10_slab_vac5A_relaxed_20261020"
BACKUP_DIR="/content/drive/MyDrive/MD_backup/2H-SiC_10-10_slab_vac5A_relaxed_20261020"
mkdir -p "$BACKUP_DIR"
while true; do
    cp "$WORK_DIR"/*.lammpstrj "$BACKUP_DIR/" 2>/dev/null || true
    cp "$WORK_DIR"/*.xyz "$BACKUP_DIR/" 2>/dev/null || true
    cp "$WORK_DIR"/*.log "$BACKUP_DIR/" 2>/dev/null || true
    cp "$WORK_DIR"/*.pwo "$BACKUP_DIR/" 2>/dev/null || true
    cp "$WORK_DIR"/*.pwi "$BACKUP_DIR/" 2>/dev/null || true
    cp "$WORK_DIR"/nohup.out "$BACKUP_DIR/" 2>/dev/null || true
    sleep 300
done' > backup.log 2>&1 &

echo "🚀 真空層 5.0Å スラブモデルの第一原理構造緩和計算がスタートしました！"
echo "ログ確認: tail -f $WORK_DIR/nohup.out"
echo "QEログ確認: tail -f $WORK_DIR/espresso.pwo"
echo "LAMMPSログ確認: tail -f $WORK_DIR/log.lammps"
