#!/usr/bin/env python3
import subprocess
import sys

cmd = sys.argv[1] if len(sys.argv) > 1 else "nvidia-smi"
ssh_cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", "colab", cmd]
print(f"Executing: {' '.join(ssh_cmd)}")
try:
    res = subprocess.run(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
    print("EXIT:", res.returncode)
except subprocess.TimeoutExpired:
    print("TIMEOUT expired!")
