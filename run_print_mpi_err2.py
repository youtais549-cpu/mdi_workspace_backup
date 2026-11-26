import pexpect
import sys

with open("run_print_mpi_err2.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "cat > /content/print_mpi_err2.c && export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi; export OPAL_DATADIR=$OPAL_PREFIX/share; export PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/bin:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/bin:$PATH; export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH; mpicc /content/print_mpi_err2.c -o /content/print_mpi_err2 && /opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/bin/mpirun --allow-run-as-root -np 1 /content/print_mpi_err2"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        with open("print_mpi_err2.c", "r") as src:
            child.sendline('mypassword')
            child.send(src.read())
            child.sendline('\x04') # EOF
        child.expect(pexpect.EOF, timeout=20)
