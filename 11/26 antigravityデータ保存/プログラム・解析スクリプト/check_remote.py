#!/usr/bin/env python3
import subprocess

cmd = "nvidia-smi && ps aux | grep -E 'pw.x|run_bulk' | grep -v grep && tail -n 25 /content/SiC_4periods_true_bulk_scf/espresso.pwo 2>/dev/null || true"
ssh_cmd = ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", "colab", cmd]

try:
    res = subprocess.run(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
    with open("/home/yamazaki/mdi_workspace_backup/colab_status.txt", "w") as f:
        f.write("=== STDOUT ===\n")
        f.write(res.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(res.stderr)
        f.write(f"\n=== EXIT CODE: {res.returncode} ===\n")
except Exception as e:
    with open("/home/yamazaki/mdi_workspace_backup/colab_status.txt", "w") as f:
        f.write(f"ERROR: {e}\n")
