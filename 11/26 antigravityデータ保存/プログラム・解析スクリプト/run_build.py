import pexpect
import sys

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

cmd = '''ssh colab "export LD_LIBRARY_PATH=/usr/lib64-nvidia:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/cuda/12.2/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:$LD_LIBRARY_PATH ; export PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/bin:$PATH ; cd /content/q-e/build && cmake -DCMAKE_C_COMPILER=nvc -DCMAKE_Fortran_COMPILER=nvfortran -DQE_ENABLE_CUDA=ON -DNVFORTRAN_CUDA_CC=75 -DQE_ENABLE_MPI=OFF -DCMAKE_INSTALL_PREFIX=/content/bin .."'''

check_cmd(cmd)
