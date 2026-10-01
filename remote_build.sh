#!/bin/bash
export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7
export PATH=$NVHPC_HOME/comm_libs/12.5/hpcx/hpcx-2.19/ompi/bin:$NVHPC_HOME/compilers/bin:$PATH
export LD_LIBRARY_PATH=$NVHPC_HOME/comm_libs/12.5/hpcx/hpcx-2.19/ompi/lib:$NVHPC_HOME/compilers/lib:$LD_LIBRARY_PATH

echo "Compiling Quantum ESPRESSO with GPU..."
cd /content
rm -rf q-e
git clone https://gitlab.com/QEF/q-e.git
cd q-e
git checkout qe-7.3
./configure --with-cuda="yes" --with-cuda-cc=75  # T4 only to save time
make pw -j$(nproc)
cp bin/pw.x /content/drive/MyDrive/mdi_binaries/pw.x
cp bin/pw.x /content/bin/pw.x
echo "QE Compilation done!"
