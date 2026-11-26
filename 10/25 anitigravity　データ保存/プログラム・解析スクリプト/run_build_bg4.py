import pexpect
import sys

def check_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    child.logfile_read = sys.stdout
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=10)

check_cmd('scp build_qe_cmake_fixed.sh colab:/content/build_qe_cmake_fixed.sh')
check_cmd('ssh colab "nohup bash /content/build_qe_cmake_fixed.sh > /content/build_qe.log 2>&1 &"')
