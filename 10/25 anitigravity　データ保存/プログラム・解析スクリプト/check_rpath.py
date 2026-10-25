import pexpect
import sys

child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "objdump -x /content/bin/lmp | grep RPATH; objdump -x /content/bin/lmp | grep RUNPATH"', encoding='utf-8')
index = child.expect(['password:', pexpect.EOF], timeout=10)
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF, timeout=10)

print(child.before)
