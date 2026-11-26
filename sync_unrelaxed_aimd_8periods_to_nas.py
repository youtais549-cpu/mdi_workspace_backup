#!/usr/bin/env python3
"""
sync_unrelaxed_aimd_8periods_to_nas.py
==============================================================================
NAS (\\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法) に
"{101_0}8周期3.0Å構造最適化なしtest run" フォルダを作成し、
構造最適化なし初期構造からの 300 K NVT-AIMD (100 steps) の全データを保存するスクリプト
==============================================================================
"""
import subprocess
import base64

ps_script = r"""
$ErrorActionPreference = "Stop"
$nasRoot = "\\192.168.12.69\Results\yamazaki\research"
$aimdRoot = Join-Path $nasRoot "第一原理分子動力学法"
$targetDir = Join-Path $aimdRoot "{101_0}8周期3.0Å構造最適化なしtest run"

New-Item -ItemType Directory -Force -Path $aimdRoot | Out-Null
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$wslRoot = "\\wsl.localhost\Ubuntu\home\WORKSTATION4WSL\.gemini\antigravity\scratch\mdi_workspace_backup"
$unrelWsl = Join-Path $wslRoot "aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080"

if (Test-Path -LiteralPath (Join-Path $wslRoot "run_8periods_vac3.0A_unrelaxed_aimd_100steps.py")) {
    Copy-Item -LiteralPath (Join-Path $wslRoot "run_8periods_vac3.0A_unrelaxed_aimd_100steps.py") -Destination $targetDir -Force
}

if (Test-Path -LiteralPath $unrelWsl) {
    Get-ChildItem -LiteralPath $unrelWsl -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $targetDir -Force
    }
}

Write-Host "=== Target NAS Directory: $targetDir ==="
Get-ChildItem -LiteralPath $targetDir | Select-Object Name, Length
"""

enc = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")
res = subprocess.run(
    ["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-NoProfile", "-EncodedCommand", enc],
    capture_output=True,
    timeout=120,
)
print(res.stdout.decode("cp932", errors="replace"))
if res.stderr:
    print("STDERR:", res.stderr.decode("cp932", errors="replace"))

