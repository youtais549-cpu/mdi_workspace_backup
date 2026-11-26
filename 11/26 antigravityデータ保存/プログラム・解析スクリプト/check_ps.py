import pexpect
import sys

child = pexpect.spawn('ssh colab "ps aux | grep pw.x"', encoding='utf-8')
child.logfile_read = sys.stdout
index = child.expect(['password:', pexpect.EOF], timeout=10)
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF, timeout=10)
