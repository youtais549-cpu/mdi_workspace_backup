import pexpect
import sys

with open("search_ompi_err.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi; export OPAL_DATADIR=$OPAL_PREFIX/share; export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH; grep -rn 9035 /opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi/include"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=20)
