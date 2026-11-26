#!/usr/bin/env python3
"""
sync_aimd_8periods_to_nas.py
==============================================================================
NAS (\\192.168.12.69\Results\yamazaki\research) へのフォルダ作成および
8周期・真空3.0Å AIMD テストランのデータ・実行コード同期スクリプト
  1. \\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法\{101_0}８周期3.0Åtest run
  2. \\192.168.12.69\Results\yamazaki\research\実行コード\{101_0}８周期3.0Åtest runコード
==============================================================================
"""
import subprocess
import base64

ps_script = r"""
$ErrorActionPreference = "Stop"
$nasRoot = "\\192.168.12.69\Results\yamazaki\research"
$aimdRoot = Join-Path $nasRoot "第一原理分子動力学法"
$dataDir = Join-Path $aimdRoot "{101_0}８周期3.0Åtest run"
$codeDir = Join-Path (Join-Path $nasRoot "実行コード") "{101_0}８周期3.0Åtest runコード"

New-Item -ItemType Directory -Force -Path $aimdRoot | Out-Null
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
New-Item -ItemType Directory -Force -Path $codeDir | Out-Null

$wslRoot = "\\wsl.localhost\Ubuntu\home\WORKSTATION4WSL\.gemini\antigravity\scratch\mdi_workspace_backup"
$relaxWsl = Join-Path $wslRoot "calc_2H-SiC_10-10_8periods_vac3.0A_rtx5080"
$aimdWsl = Join-Path $wslRoot "aimd_2H-SiC_10-10_8periods_vac3.0A_300K_100steps_rtx5080"

# 1. 実行コードフォルダへのコピー
$codeFiles = @(
    (Join-Path $wslRoot "run_8periods_vac3.0A_relax_and_aimd_100steps.py"),
    (Join-Path $relaxWsl "qe_mdi_engine_rtx5080.py"),
    (Join-Path $relaxWsl "dft_settings.py"),
    (Join-Path $relaxWsl "in.lammps.optimized_conv"),
    (Join-Path $relaxWsl "slab_10-10_288atoms_vac3.0A_init.data")
)
foreach ($f in $codeFiles) {
    if (Test-Path -LiteralPath $f) {
        Copy-Item -LiteralPath $f -Destination $codeDir -Force
    }
}
if (Test-Path -LiteralPath (Join-Path $aimdWsl "in.lammps")) {
    Copy-Item -LiteralPath (Join-Path $aimdWsl "in.lammps") -Destination (Join-Path $codeDir "in.lammps.aimd_300K_100steps") -Force
}
if (Test-Path -LiteralPath (Join-Path $aimdWsl "slab_10-10_288atoms_vac3.0A_relaxed.data")) {
    Copy-Item -LiteralPath (Join-Path $aimdWsl "slab_10-10_288atoms_vac3.0A_relaxed.data") -Destination $codeDir -Force
}

# 2. データ保存フォルダ ({101_0}８周期3.0Åtest run) へのコピー
$relaxDest = Join-Path $dataDir "01_0K_構造最適化_初期構造作成"
$aimdDest  = Join-Path $dataDir "02_300K_NVT_AIMD_100steps"
New-Item -ItemType Directory -Force -Path $relaxDest | Out-Null
New-Item -ItemType Directory -Force -Path $aimdDest | Out-Null

if (Test-Path -LiteralPath $relaxWsl) {
    Get-ChildItem -LiteralPath $relaxWsl -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $relaxDest -Force
    }
}
if (Test-Path -LiteralPath $aimdWsl) {
    Get-ChildItem -LiteralPath $aimdWsl -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $aimdDest -Force
    }
    # トップ階層にも主要な結果ファイルを配置
    Get-ChildItem -LiteralPath $aimdWsl -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $dataDir -Force
    }
}

Write-Host "=== [1] Code Directory: $codeDir ==="
Get-ChildItem -LiteralPath $codeDir | Select-Object Name, Length
Write-Host "=== [2] Data Directory: $dataDir ==="
Get-ChildItem -LiteralPath $dataDir | Select-Object Name, Length
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

