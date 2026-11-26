import pexpect
import sys

port = 10174
host = "2.tcp.ngrok.io"
password = "mypassword"

cmd = f"ssh -o StrictHostKeyChecking=no -p {port} root@{host}"
child = pexpect.spawn(cmd, encoding='utf-8')

# Wait for either password prompt or failure
i = child.expect(["password:", pexpect.EOF, pexpect.TIMEOUT], timeout=15)
if i != 0:
    print(f"Failed to connect. Output: {child.before}")
    sys.exit(1)

child.sendline(password)
child.expect("#")
print("Connected successfully!")

def run_cmd(c):
    print(f"> {c}")
    child.sendline(c)
    child.expect("#")
    print(child.before)

run_cmd("ls -lh /content/")
run_cmd("pip install ase pymdi")
run_cmd("mkdir -p /content/bin; cp /content/drive/MyDrive/mdi_binaries/* /content/bin/; chmod +x /content/bin/*")
run_cmd("mkdir -p /content/SiC_3x3x10_MD; cp -f /content/drive/MyDrive/SiC_MD_backup/* /content/SiC_3x3x10_MD/")
run_cmd("cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > nohup.out 2>&1 &")
run_cmd("sleep 3")
run_cmd("cat /content/SiC_3x3x10_MD/nohup.out")
