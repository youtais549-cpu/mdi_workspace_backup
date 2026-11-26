import pexpect
import sys
import os

with open(os.path.expanduser('~/.ssh/id_ed25519.pub'), 'r') as f:
    pub_key = f.read().strip()

child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "mkdir -p ~/.ssh && echo \'' + pub_key + '\' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"', encoding='utf-8')
index = child.expect(['password:', pexpect.EOF], timeout=10)
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF, timeout=10)
print("Key copied")
