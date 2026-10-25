import pexpect

child = pexpect.spawn('ssh-copy-id -o StrictHostKeyChecking=no colab', encoding='utf-8', timeout=60)
index = child.expect(['password:', pexpect.EOF, pexpect.TIMEOUT])
if index == 0:
    child.sendline('mypassword')
    child.expect(pexpect.EOF)
    print(child.before)
