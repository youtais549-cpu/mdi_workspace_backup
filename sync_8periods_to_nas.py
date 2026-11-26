#!/usr/bin/env python3
r"""
sync_8periods_to_nas.py
8周期・真空層5Åの全計算データ ({101_0}8周期５Å) を
NAS (\\192.168.12.69\Results\yamazaki\research\{101_0}8周期５Å) へ安全に保存するスクリプト
"""
import os
import sys
import base64
import shutil
import subprocess

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
FOLDER_NAME = "{101_0}8周期５Å"
SRC_DIR = os.path.join(WORKSPACE_DIR, FOLDER_NAME)


def copy_via_powershell_encoded():
    ps_bin = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    if not os.path.exists(ps_bin):
        print("[Error] Windows PowerShell not found at /mnt/c/...")
        return False

    print("[Step 1] Staging files to /mnt/c/temp_sic_sync/stage_8periods ...")
    stage_root = "/mnt/c/temp_sic_sync"
    stage_dir = os.path.join(stage_root, "stage_8periods")
    os.makedirs(stage_root, exist_ok=True)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    shutil.copytree(SRC_DIR, stage_dir)

    # PowerShell スクリプトを UTF-16LE Base64 (-EncodedCommand) で渡すことで
    # 全角文字「{101_0}8周期５Å」の文字化けを100%防止し、-LiteralPath の '*' 問題も回避する
    ps_script = f"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$src = 'C:\\temp_sic_sync\\stage_8periods'
$dstParent = '\\\\192.168.12.69\\Results\\yamazaki\\research'
$folderName = '{FOLDER_NAME}'
$dst = Join-Path $dstParent $folderName

# 先ほど文字化けして作られた空フォルダがあれば削除
Get-ChildItem -LiteralPath $dstParent -Directory | Where-Object {{
    $_.Name -like '{{101_0}}8*' -and $_.Name -ne $folderName
}} | ForEach-Object {{
    if ((Get-ChildItem -LiteralPath $_.FullName).Count -eq 0) {{
        Remove-Item -LiteralPath $_.FullName -Force
    }}
}}

if (!(Test-Path -LiteralPath $dst)) {{
    New-Item -ItemType Directory -Path $dst -Force | Out-Null
}}

Get-ChildItem -LiteralPath $src | ForEach-Object {{
    Copy-Item -LiteralPath $_.FullName -Destination $dst -Recurse -Force
}}

$files = Get-ChildItem -LiteralPath $dst -File
Write-Output ("TARGET_DIR=" + $dst)
Write-Output ("COPIED_COUNT=" + $files.Count)
$files | Select-Object -First 15 | ForEach-Object {{ Write-Output ("  - " + $_.Name + " (" + $_.Length + " bytes)") }}
"""
    encoded_cmd = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")

    print(f"[Step 2] Copying to \\\\192.168.12.69\\Results\\yamazaki\\research\\{FOLDER_NAME} ...")
    res = subprocess.run(
        [ps_bin, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_cmd],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    print(res.stdout)
    if res.returncode == 0 and "COPIED_COUNT=" in res.stdout and "COPIED_COUNT=0" not in res.stdout:
        print("✅ NAS への全ファイル保存が完了しました！")
        return True
    else:
        print(f"❌ Error (code={res.returncode}): {res.stderr}")
        return False


if __name__ == "__main__":
    if not os.path.exists(SRC_DIR):
        print(f"❌ Source directory not found: {SRC_DIR}")
        sys.exit(1)

    if copy_via_powershell_encoded():
        sys.exit(0)
    sys.exit(1)
