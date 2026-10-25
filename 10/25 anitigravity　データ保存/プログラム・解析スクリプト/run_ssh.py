import pexpect
import sys

import time

def run_ssh_commands():
    child = pexpect.spawn('ssh colab', encoding='utf-8', timeout=60)
    
    try:
        index = child.expect(['password:', 'Are you sure you want to continue connecting', r'.*#', pexpect.EOF, pexpect.TIMEOUT])
        
        if index == 0:
            child.sendline('mypassword')
        elif index == 1:
            child.sendline('yes')
            child.expect('password:')
            child.sendline('mypassword')
        elif index == 2:
            pass # Already logged in
        else:
            print(f"Failed to connect: {child.before}")
            return
            
        child.expect(r'.*#')
        
        commands = [
            "mkdir -p /content/SiC_3x3x10_MD",
            "cp -r /content/drive/MyDrive/SiC_MD_backup/* /content/SiC_3x3x10_MD/ 2>/dev/null || true",
            "cd /content/SiC_3x3x10_MD",
            "nohup bash run_colab.sh > nohup.out 2>&1 &",
            "nohup bash -c 'while true; do cp /content/SiC_3x3x10_MD/*.lammpstrj /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/*.pwo /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/qe_engine.log /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; sleep 300; done' > backup_nohup.out 2>&1 &",
            "echo 'Simulation started. Tailing log...'",
            "sleep 3",
            "tail -f nohup.out"
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            child.sendline(cmd)
            if cmd.startswith("tail -f"):
                child.logfile_read = sys.stdout
                child.expect(pexpect.EOF, timeout=None)
            else:
                child.expect(r'.*#')
                print(child.before)
            
        child.sendline('exit')
        child.expect(pexpect.EOF)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Current output: {child.before}")

if __name__ == '__main__':
    run_ssh_commands()
