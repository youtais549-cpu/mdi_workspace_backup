#!/usr/bin/env python3
r"""
sync_all_periods_to_nas.py
==============================================================================
nas_staging_periods/ に生成された周期数スラブモデルの各条件フォルダ
({101_0}1周期5Å, {101_0}3周期5Å, {101_0}5周期5Å, {101_0}7周期5Å, {101_0}9周期5Å, {101_0}10周期5Å など)
および集計グラフ・CSVを NAS (\\192.168.12.69\Results\yamazaki\research\) へ一括転送・保存するスクリプト
==============================================================================
"""
import os
import sys
import base64
import shutil
import subprocess

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
NAS_LOCAL_STAGING_ROOT = os.path.join(WORKSPACE_DIR, "nas_staging_periods")


def sync_all_to_nas():
    if not os.path.exists(NAS_LOCAL_STAGING_ROOT):
        print(f"❌ Staging directory not found: {NAS_LOCAL_STAGING_ROOT}")
        return False

    ps_bin = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    if not os.path.exists(ps_bin):
        print(f"❌ Windows PowerShell not found at {ps_bin}")
        return False

    folders = sorted(
        [d for d in os.listdir(NAS_LOCAL_STAGING_ROOT) if os.path.isdir(os.path.join(NAS_LOCAL_STAGING_ROOT, d))]
    )
    if not folders:
        print("❌ No staged folders found in nas_staging_periods.")
        return False

    stage_win_root = "/mnt/c/temp_sic_sync/sweep_periods_all"
    if os.path.exists(stage_win_root):
        shutil.rmtree(stage_win_root)
    os.makedirs(stage_win_root, exist_ok=True)

    print(f"📦 Staging {len(folders)} folders to {stage_win_root}...")
    for folder in folders:
        src_path = os.path.join(NAS_LOCAL_STAGING_ROOT, folder)
        dst_path = os.path.join(stage_win_root, folder)
        shutil.copytree(src_path, dst_path)

    # 周期数集計グラフとCSVもWindows側にステージング
    summary_files = [
        "surface_energy_vs_periods_plot_data.csv",
        "周期数と表面破壊エネルギーの関係.png",
        "周期数と表面破壊エネルギーの関係.pdf",
        "周期数と表面破壊エネルギーの関係.svg",
    ]
    for fn in summary_files:
        src = os.path.join(WORKSPACE_DIR, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(stage_win_root, fn))

    ps_script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$srcRoot = 'C:\temp_sic_sync\sweep_periods_all'
$dstParent = '\\192.168.12.69\Results\yamazaki\research'

# 各周期数フォルダを同期
Get-ChildItem -LiteralPath $srcRoot -Directory | ForEach-Object {
    $folderName = $_.Name
    $srcDir = $_.FullName
    $dstDir = Join-Path $dstParent $folderName
    if (!(Test-Path -LiteralPath $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }
    Get-ChildItem -LiteralPath $srcDir | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $dstDir -Recurse -Force
    }
    $count = (Get-ChildItem -LiteralPath $dstDir -File).Count
    Write-Output ("SYNCED FOLDER: " + $dstDir + " (" + $count + " files)")
}

# ルート直下に集計ファイル群を同期
Get-ChildItem -LiteralPath $srcRoot -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $dstParent -Force
    Write-Output ("SYNCED ROOT FILE: " + $_.Name)
}
"""
    encoded_cmd = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
    res = subprocess.run(
        [ps_bin, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_cmd],
        text=True,
        capture_output=True,
        encoding="cp932",
        errors="replace",
    )
    print(res.stdout)
    if res.returncode == 0 and "SYNCED" in res.stdout:
        print(f"✅ All {len(folders)} folders and summary files synced to NAS successfully!")
        return True
    else:
        print(f"❌ NAS sync failed (code={res.returncode}): {res.stderr}")
        return False


if __name__ == "__main__":
    if sync_all_to_nas():
        sys.exit(0)
    sys.exit(1)

