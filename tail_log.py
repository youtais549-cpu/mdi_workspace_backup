import pexpect
import sys

child = pexpect.spawn('ssh colab "tail -f /content/SiC_3x3x10_MD/nohup.out"', encoding='utf-8')
child.logfile_read = sys.stdout
index = child.expect(['password:', pexpect.EOF], timeout=None)
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF, timeout=None)
