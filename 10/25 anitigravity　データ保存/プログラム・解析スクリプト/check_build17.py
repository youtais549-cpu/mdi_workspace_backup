import pexpect
import sys
import time

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

check_cmd('ssh colab "ls -l /content/q-e/build/bin/pw.x"')
check_cmd('ssh colab "cp /content/q-e/build/bin/pw.x /content/bin/pw.x"')
