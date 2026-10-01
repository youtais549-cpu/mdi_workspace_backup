import pexpect
import sys

with open("check_pwx_nompirun.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "env LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib /content/bin/pw.x -v"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=20)
