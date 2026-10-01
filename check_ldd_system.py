import pexpect
import sys

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

check_cmd('ssh colab "file /content/bin/pw.x"')
check_cmd('ssh colab "ls -la /content/drive/MyDrive/mdi_binaries/pw.x"')
