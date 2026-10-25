import pexpect
import sys
import time
import os

nas_dir = "/mnt/nas_backup/SiC_3x3x10_MD"
os.makedirs(nas_dir, exist_ok=True)

print("Starting continuous NAS backup...")
while True:
    try:
        print("Syncing Colab to NAS...")
        child = pexpect.spawn(f'scp -r colab:/content/SiC_3x3x10_MD/ {nas_dir}', encoding='utf-8')
        index = child.expect(['password:', pexpect.EOF], timeout=30)
        if index == 0:
            child.sendline('mypassword')
            child.expect(pexpect.EOF, timeout=600)
        print("NAS Backup completed successfully.")
    except Exception as e:
        print(f"Error during NAS backup: {e}")
    time.sleep(300)
