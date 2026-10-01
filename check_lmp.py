import pexpect
import sys

child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "env OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi /content/bin/lmp -h"', encoding='utf-8')
index = child.expect(['password:', pexpect.EOF], timeout=10)
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF, timeout=10)

print(child.before)
