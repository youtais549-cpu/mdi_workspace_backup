#!/usr/bin/env python3
r"""
sync_all_2periods_to_nas.py
ワークスペース内の nas_staging_2periods/ に生成された
2周期モデルの全真空層条件フォルダ ({101_0}2周期0.5Å 〜 {101_0}2周期10Å) を
NAS (\\192.168.12.69\Results\yamazaki\research\{101_0}2周期〇Å) へ一括転送・保存するスクリプト
"""
import os
import sys
import base64
import shutil
import subprocess

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
NAS_LOCAL_STAGING_ROOT = os.path.join(WORKSPACE_DIR, "nas_staging_2periods")


def sync_all_to_nas():
    if not os.path.exists(NAS_LOCAL_STAGING_ROOT):
        print(f"❌ Staging directory not found: {NAS_LOCAL_STAGING_ROOT}")
        return False

    ps_bin = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    if not os.path.exists(ps_bin):
        print("❌ Windows PowerShell not found at /mnt/c/...")
        return False

    folders = sorted(
        [d for d in os.listdir(NAS_LOCAL_STAGING_ROOT) if os.path.isdir(os.path.join(NAS_LOCAL_STAGING_ROOT, d))]
    )
    if not folders:
        print("❌ No staged folders found in nas_staging_2periods.")
        return False

    stage_win_root = "/mnt/c/temp_sic_sync/sweep_2periods_all"
    if os.path.exists(stage_win_root):
        shutil.rmtree(stage_win_root)
    os.makedirs(stage_win_root, exist_ok=True)

    for folder in folders:
        shutil.copytree(os.path.join(NAS_LOCAL_STAGING_ROOT, folder), os.path.join(stage_win_root, folder))

    ps_script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$srcRoot = 'C:\temp_sic_sync\sweep_2periods_all'
$dstParent = '\\192.168.12.69\Results\yamazaki\research'

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
    Write-Output ("SYNCED: " + $dstDir + " (" + $count + " files)")
}
"""
    encoded_cmd = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
    res = subprocess.run(
        [ps_bin, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_cmd],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    print(res.stdout)
    if res.returncode == 0 and "SYNCED:" in res.stdout:
        print(f"✅ All {len(folders)} folders synced to NAS successfully!")
        return True
    else:
        print(f"❌ NAS sync failed (code={res.returncode}): {res.stderr}")
        return False


if __name__ == "__main__":
    if sync_all_to_nas():
        sys.exit(0)
    sys.exit(1)

