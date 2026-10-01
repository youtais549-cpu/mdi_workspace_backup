import pexpect
child = pexpect.spawn('ssh colab', encoding='utf-8')
child.logfile = open("test_ssh.log", "w")
try:
    child.expect(r'.*#', timeout=10)
    print("Success")
except pexpect.TIMEOUT:
    print("Timeout")
except pexpect.EOF:
    print("EOF")
