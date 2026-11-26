#!/usr/bin/env python3
r"""
sync_bulk2_aimd_8periods_to_nas.py
==============================================================================
NAS (\\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法\{101_0}8周期3.0Å構造最適化なしtest run) に
"バルクモデル2" フォルダを作成し、
8周期バルクモデルの 300 K NVT-AIMD (Step 300 から完全引き継ぎ・追加 300 steps -> 通算 600 steps)
の全データを同期・保存するスクリプト
==============================================================================
"""
import subprocess
import base64

ps_script = r"""
$ErrorActionPreference = "Continue"
$nasRoot = "\\192.168.12.69\Results\yamazaki\research"
$aimdRoot = Join-Path $nasRoot "第一原理分子動力学法"
$parentDir = Join-Path $aimdRoot "{101_0}8周期3.0Å構造最適化なしtest run"
$targetDir = Join-Path $parentDir "バルクモデル2"

New-Item -ItemType Directory -Force -Path $aimdRoot | Out-Null
New-Item -ItemType Directory -Force -Path $parentDir | Out-Null
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$wslRoot = "\\wsl.localhost\Ubuntu\home\WORKSTATION4WSL\.gemini\antigravity\scratch\mdi_workspace_backup"
$bulk2Wsl = Join-Path $wslRoot "aimd_2H-SiC_10-10_8periods_bulk_300K_600steps_rtx5080"

if (Test-Path -LiteralPath (Join-Path $wslRoot "run_8periods_bulk_aimd_continue_to_600steps.py")) {
    Copy-Item -LiteralPath (Join-Path $wslRoot "run_8periods_bulk_aimd_continue_to_600steps.py") -Destination $targetDir -Force
}

if (Test-Path -LiteralPath $bulk2Wsl) {
    Get-ChildItem -LiteralPath $bulk2Wsl -File | ForEach-Object {
        # Skip temporary 20MB cache file if needed, or copy all result files
        if ($_.Name -ne "prev_300steps_espresso_all_steps.pwo") {
            try {
                Copy-Item -LiteralPath $_.FullName -Destination $targetDir -Force -ErrorAction Stop
            } catch {
                Write-Host "Skipped locked/busy file:" $_.Name
            }
        }
    }
}

Write-Host "=== Target NAS Directory: $targetDir ==="
Get-ChildItem -LiteralPath $targetDir | Select-Object Name, Length
"""

enc = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")
res = subprocess.run(
    ["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-NoProfile", "-EncodedCommand", enc],
    capture_output=True,
    timeout=180,
)
print(res.stdout.decode("cp932", errors="replace"))
if res.stderr:
    print("STDERR:", res.stderr.decode("cp932", errors="replace"))

