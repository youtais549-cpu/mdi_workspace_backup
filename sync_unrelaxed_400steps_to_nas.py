#!/usr/bin/env python3
r"""
sync_unrelaxed_400steps_to_nas.py
==============================================================================
NAS (\\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法\{101_0}8周期3.0Å　構造最適化なし) に、
8周期・真空層 3.0 Å スラブモデル（構造最適化なし）の 300 K NVT-AIMD
(Step 100 から完全引き継ぎ・追加 300 steps -> 通算 400 steps)
の全データを同期・保存するスクリプト
==============================================================================
"""
import subprocess
import base64

ps_script = r"""
$ErrorActionPreference = "Continue"
$nasRoot = "\\192.168.12.69\Results\yamazaki\research"
$aimdRoot = Join-Path $nasRoot "第一原理分子動力学法"
$targetDir = Join-Path $aimdRoot "{101_0}8周期3.0Å　構造最適化なし"

New-Item -ItemType Directory -Force -Path $aimdRoot | Out-Null
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$wslRoot = "\\wsl.localhost\Ubuntu\home\WORKSTATION4WSL\.gemini\antigravity\scratch\mdi_workspace_backup"
$slab400Wsl = Join-Path $wslRoot "aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_400steps_rtx5080"

if (Test-Path -LiteralPath (Join-Path $wslRoot "run_8periods_vac3.0A_unrelaxed_aimd_continue_to_400steps.py")) {
    try {
        Copy-Item -LiteralPath (Join-Path $wslRoot "run_8periods_vac3.0A_unrelaxed_aimd_continue_to_400steps.py") -Destination $targetDir -Force -ErrorAction Stop
    } catch {
        Write-Host "Skipped locked script file"
    }
}

if (Test-Path -LiteralPath $slab400Wsl) {
    Get-ChildItem -LiteralPath $slab400Wsl -File | ForEach-Object {
        if ($_.Name -ne "prev_100steps_espresso_all_steps.pwo") {
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

