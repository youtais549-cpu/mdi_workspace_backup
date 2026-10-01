import os

ssh_dir = os.path.expanduser('~/.ssh')
config_path = os.path.join(ssh_dir, 'config')

os.makedirs(ssh_dir, exist_ok=True)

config_content = """
Host *.trycloudflare.com
    HostName %h
    User root
    Port 22
    ProxyCommand /home/yamazaki_yuta/bin/cloudflared access ssh --hostname %h
"""

# Check if already exists to avoid duplicate
exists = False
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        if 'trycloudflare.com' in f.read():
            exists = True

if not exists:
    with open(config_path, 'a') as f:
        f.write(config_content)
    print("Added cloudflare config to ~/.ssh/config")
else:
    print("Config already exists.")
