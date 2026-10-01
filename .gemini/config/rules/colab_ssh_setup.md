---
name: colab_ssh_setup
description: "Guidelines and setup scripts for connecting to Google Colab via SSH using cloudflared."
---

# Google Colab SSH Setup and Troubleshooting

When the user wants to connect to a Google Colab instance via SSH using `cloudflared`, or if they are experiencing connection freezes/timeouts (e.g., `websocket: bad handshake` or `502 Bad Gateway`), follow these guidelines:

## 1. The All-In-One Colab Setup Script
Colab often blocks `sshd` from starting automatically via `policy-rc.d`, or has IPv6 issues. Do NOT rely on third-party libraries like `colab_ssh` which can fail silently or bind to unexpected ports (like 2222).
Instead, provide the user with this robust, idempotent setup script to run in a Colab cell:

```bash
# 1. Reinstall openssh-server to reset configs
!apt-get update -qq && apt-get install -y openssh-server -qq

# 2. Configure SSHD (Set password, fix IPv6 binding issues)
!mkdir -p /var/run/sshd
!echo 'root:mypassword' | chpasswd
!sed -i '/ListenAddress ::/d' /etc/ssh/sshd_config
!sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
!sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
!sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# 3. Start SSH Server forcefully
!pkill -f sshd
!/usr/sbin/sshd

# 4. Start Cloudflared tunnel on IPv4 port 22
!pkill -f cloudflared
!wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
!chmod +x cloudflared-linux-amd64
!./cloudflared-linux-amd64 tunnel --url ssh://127.0.0.1:22
```
*Note: This cell will run continuously and output a `https://<random>.trycloudflare.com` URL.*

## 2. Local SSH Configuration
Once the user provides the new `.trycloudflare.com` URL, update their `~/.ssh/config` as follows:
```text
Host colab
    HostName <NEW_URL>
    User root
    Port 22
    ProxyCommand cloudflared access ssh --hostname %h
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
```

## 3. Pexpect / Automated Login Prompts
When using `pexpect` in Python scripts to automate SSH login to Colab, remember that the default Colab root prompt is NOT `root@...#`. It usually looks like `~#` with ANSI escape codes.
- **Incorrect regex**: `r'root@.*#'`
- **Correct regex**: `r'.*#'` or `r'~#'`
Failure to use the correct regex will cause the script to freeze until the `pexpect` timeout is reached.
