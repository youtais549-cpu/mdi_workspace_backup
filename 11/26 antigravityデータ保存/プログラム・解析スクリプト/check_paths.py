import pexpect
import sys

with open("check_paths.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "which mpirun; ldd /content/bin/lmp"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)
