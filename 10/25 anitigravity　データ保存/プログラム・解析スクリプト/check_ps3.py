import pexpect
import sys

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

check_cmd('ssh colab "ps aux | grep pw.x"')
check_cmd('ssh colab "tail -n 20 /content/SiC_3x3x10_MD/nohup.out"')
