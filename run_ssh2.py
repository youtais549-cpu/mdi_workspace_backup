import pexpect
import sys
import os
import time

def run_ssh_commands():
    # Start cloudflared in the background listening on port 2222
    os.system("/home/yamazaki_yuta/bin/cloudflared access tcp --hostname tiger-web-backed-jeff.trycloudflare.com --listener 127.0.0.1:2222 > /dev/null 2>&1 &")
    time.sleep(2) # wait for it to start
    
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -p 2222 root@127.0.0.1', encoding='utf-8', timeout=60)
    
    try:
        index = child.expect(['password:', 'Are you sure you want to continue connecting', pexpect.EOF, pexpect.TIMEOUT])
        
        if index == 1:
            child.sendline('yes')
            child.expect('password:')
            child.sendline('mypassword')
        elif index == 0:
            child.sendline('mypassword')
        else:
            print(f"Failed to connect: {child.before}")
            return
            
        child.expect(r'root@.*#')
        print("Successfully connected!")
        
        commands = [
            "ls -la /content"
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            child.sendline(cmd)
            child.expect(r'root@.*#')
            print(child.before)
            
        child.sendline('exit')
        child.expect(pexpect.EOF)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Current output: {child.before}")
    finally:
        os.system("pkill -f cloudflared")

if __name__ == '__main__':
    run_ssh_commands()
