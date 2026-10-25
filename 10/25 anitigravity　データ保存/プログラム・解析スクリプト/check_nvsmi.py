import pexpect
import sys

child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "LD_LIBRARY_PATH=/usr/lib64-nvidia:/usr/local/cuda/lib64 nvidia-smi"', encoding='utf-8')
index = child.expect(['password:', pexpect.EOF], timeout=10)
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF, timeout=10)
print(child.before)
