import subprocess
import sys
import os

def run_interactive(cmd):
    print(f"\n--- Running: {cmd} ---")
    subprocess.run(cmd, shell=True)

print("1. Uploading local files to Colab...")
run_interactive('ssh colab "mkdir -p /content/SiC_3x3x10_MD"')
run_interactive('scp -O -r /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/ colab:/content/')

print("\n2. Killing old calculation if running...")
run_interactive('ssh colab "killall -9 pw.x lmp 2>/dev/null || true"')

print("\n3. Starting calculation on Colab...")
run_interactive('ssh colab "cd /content/SiC_3x3x10_MD && nohup bash master_run_cpu.sh > master.log 2>&1 &"')

print("\n4. Tailing log...")
try:
    subprocess.run('ssh colab "tail -f /content/SiC_3x3x10_MD/nohup.out"', shell=True)
except KeyboardInterrupt:
    pass
