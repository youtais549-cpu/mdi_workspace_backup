import pexpect
import sys

script = """#!/bin/bash
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
"""

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

with open('remote_build.sh', 'w') as f:
    f.write(script)

check_cmd('scp remote_build.sh colab:/content/build_qe.sh')
check_cmd('ssh colab "bash /content/build_qe.sh > /content/build_qe.log 2>&1 &"')
