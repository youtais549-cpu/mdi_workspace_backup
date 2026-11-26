import pexpect
import sys

def run_cmd(cmd):
    child = pexpect.spawn(cmd, encoding='utf-8')
    index = child.expect(['password:', 'Are you sure you want to continue connecting', pexpect.EOF])
    if index == 1:
        child.sendline('yes')
        child.expect('password:')
        child.sendline('mypassword')
    elif index == 0:
        child.sendline('mypassword')
    child.expect(pexpect.EOF)
    print(child.before)

print("Copying files to Colab...")
run_cmd('scp -r /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD colab:/content/')

print("Starting master_run.sh on Colab...")
run_cmd('ssh colab "cd /content/SiC_3x3x10_MD && bash master_run.sh"')
