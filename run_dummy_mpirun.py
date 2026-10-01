import pexpect
import sys

with open("run_dummy_mpirun.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "cd /content/SiC_3x3x10_MD && export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi; export OPAL_DATADIR=$OPAL_PREFIX/share; export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH; /opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/bin/mpirun --allow-run-as-root -np 1 /content/bin/pw.x < dummy.pwi > dummy2.pwo 2>&1; cat dummy2.pwo"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=60)
