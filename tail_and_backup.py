import pexpect
import sys
import time

print("Tailing log from Colab. Press Ctrl+C to stop.")
child = pexpect.spawn('ssh colab "tail -f /content/SiC_3x3x10_MD/qe_engine.log /content/SiC_3x3x10_MD/nohup.out"', encoding='utf-8')
child.logfile_read = sys.stdout
index = child.expect(['password:', pexpect.EOF], timeout=10)
if index == 0:
    child.sendline('mypassword')

try:
    child.expect(pexpect.EOF, timeout=None)
except KeyboardInterrupt:
    print("\nStopped tailing.")
