import pexpect
import sys

with open("check_pwo_head.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "head -n 50 /content/SiC_3x3x10_MD/espresso.pwo"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=20)
