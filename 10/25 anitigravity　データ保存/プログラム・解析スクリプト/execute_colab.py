import pexpect
import sys

child = pexpect.spawn('ssh colab', encoding='utf-8', timeout=60)
child.logfile_read = sys.stdout

try:
    index = child.expect(['password:', 'Are you sure you want to continue connecting'])
    if index == 1:
        child.sendline('yes')
        child.expect('password:')
    child.sendline('mypassword')
    
    child.expect(r'.*#')
    
    # 1. Execute master_run.sh
    child.sendline('cd /content/SiC_3x3x10_MD && bash master_run.sh')
    child.expect(r'.*#')
    
    child.sendline('exit')
except Exception as e:
    print(f"Error: {e}")

