#!/usr/bin/env python3
"""
copy_unrelaxed_code_to_nas.py
"""
import subprocess
import base64

ps_script = r"""
$ErrorActionPreference = 'Stop'
$nasRoot = '\\192.168.12.69\Results\yamazaki\research\実行コード'
$targetFolder = Join-Path $nasRoot '{101_0}8周期3.0Å構造最適化なし　test run'

New-Item -ItemType Directory -Force -Path $targetFolder | Out-Null

$wslRoot = '\\wsl.localhost\Ubuntu\home\WORKSTATION4WSL\.gemini\antigravity\scratch\mdi_workspace_backup'
$unrelWsl = Join-Path $wslRoot 'aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080'

$filesToCopy = @(
    (Join-Path $wslRoot 'run_8periods_vac3.0A_unrelaxed_aimd_100steps.py'),
    (Join-Path $unrelWsl 'qe_mdi_engine_rtx5080.py'),
    (Join-Path $unrelWsl 'dft_settings.py'),
    (Join-Path $unrelWsl 'in.lammps'),
    (Join-Path $unrelWsl 'slab_10-10_288atoms_vac3.0A_unrelaxed.data'),
    (Join-Path $unrelWsl 'make_xyz.py'),
    (Join-Path $unrelWsl 'auto_generate_progression_graphs.py')
)

foreach ($item in $filesToCopy) {
    if (Test-Path -LiteralPath $item) {
        Copy-Item -LiteralPath $item -Destination $targetFolder -Force
    }
}

Write-Host "=== Copied Files to NAS: $targetFolder ==="
Get-ChildItem -LiteralPath $targetFolder | Select-Object Name, Length
"""

enc = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
res = subprocess.run(
    ['/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', '-NoProfile', '-EncodedCommand', enc],
    capture_output=True,
    timeout=120,
)
print(res.stdout.decode('cp932', errors='replace'))
if res.stderr:
    print('STDERR:', res.stderr.decode('cp932', errors='replace'))

