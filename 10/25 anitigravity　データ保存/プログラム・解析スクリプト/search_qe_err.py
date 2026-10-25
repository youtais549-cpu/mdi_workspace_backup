import pexpect
import sys

with open("search_qe_err.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "cd /content/q-e-qe-7.3 && grep -rn \'9035\' ."', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=20)
