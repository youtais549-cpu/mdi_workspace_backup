import pexpect
import sys

with open("check_pwx_manual.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi; export OPAL_DATADIR=$OPAL_PREFIX/share; export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH; /content/bin/pw.x < /content/SiC_3x3x10_MD/espresso.pwi"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=30)
