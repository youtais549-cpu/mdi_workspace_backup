import pexpect
import sys

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

check_cmd('ssh colab "env OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib /opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/bin/mpirun --allow-run-as-root -np 1 /content/bin/pw.x < /dev/null"')
