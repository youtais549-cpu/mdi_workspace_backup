import os
import subprocess
import base64

files = [
    "vacuum_sweep_2periods_0.5_to_10A_results.csv",
    "vacuum_sweep_2periods_results.csv",
    "真空層の厚さと表面破壊エネルギーの関係_デフォルト仕様.png",
    "真空層の厚さと表面破壊エネルギーの関係_デフォルト仕様.pdf",
    "真空層の厚さと表面破壊エネルギーの関係_デフォルト仕様.svg",
    "真空層の厚さと表面破壊エネルギーの関係_全域表示仕様.png",
    "真空層の厚さと表面破壊エネルギーの関係_全域表示仕様.pdf",
    "真空層の厚さと表面破壊エネルギーの関係_全域表示仕様.svg",
    "真空層の厚さと表面破壊エネルギーの関係_Word最適化仕様.png",
    "真空層の厚さと表面破壊エネルギーの関係_Word最適化仕様.pdf",
    "真空層の厚さと表面破壊エネルギーの関係_Word最適化仕様.svg",
    "真空層の厚さと表面破壊エネルギーの関係_プラトー拡大仕様.png",
    "真空層の厚さと表面破壊エネルギーの関係_プラトー拡大仕様.pdf",
    "真空層の厚さと表面破壊エネルギーの関係_プラトー拡大仕様.svg",
    "SURFACE_ENERGY_RESULTS.md",
    "surface_energy_results.csv"
]

src_wsl = r"\\wsl.localhost\Ubuntu\home\WORKSTATION4WSL\.gemini\antigravity\scratch\mdi_workspace_backup"
nas_dest = r"\\192.168.12.69\Results\yamazaki\research"

ps_commands = []
for f in files:
    src_file = f"{src_wsl}\\{f}"
    dest_file = f"{nas_dest}\\{f}"
    ps_commands.append(f'if (Test-Path -LiteralPath "{src_file}") {{ Copy-Item -LiteralPath "{src_file}" -Destination "{dest_file}" -Force; Write-Host "COPIED: {f}" }}')

ps_script = "\n".join(ps_commands)
enc = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")

cmd = [
    "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
    "-NoProfile",
    "-EncodedCommand",
    enc
]

res = subprocess.run(cmd, capture_output=True, timeout=60)
out = res.stdout.decode("cp932", errors="replace")
err = res.stderr.decode("cp932", errors="replace")
print(out)
if err:
    print("STDERR:", err)
