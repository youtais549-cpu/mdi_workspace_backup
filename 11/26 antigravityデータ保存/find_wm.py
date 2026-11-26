#!/usr/bin/env python3
import subprocess

ps_code = """
$res = Get-ChildItem -Path "C:\\" -Filter "*winmostar*.exe" -Recurse -Depth 4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
if ($res) {
    Write-Host "FOUND: $res"
} else {
    Write-Host "NOT FOUND in C:\\ depth 4"
}

# Check start menu shortcuts
$shortcuts = Get-ChildItem -Path "$env:ProgramData\\Microsoft\\Windows\\Start Menu", "$env:APPDATA\\Microsoft\\Windows\\Start Menu" -Filter "*winmostar*.lnk" -Recurse -ErrorAction SilentlyContinue
foreach ($s in $shortcuts) {
    Write-Host "SHORTCUT: $($s.FullName)"
    $wsh = New-Object -ComObject WScript.Shell
    $link = $wsh.CreateShortcut($s.FullName)
    Write-Host "TARGET: $($link.TargetPath)"
}
"""

with open("/tmp/find_wm.ps1", "w", encoding="utf-8") as f:
    f.write(ps_code)

res = subprocess.run(["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "C:\\Users\\WORKSTATION4\\AppData\\Local\\Temp\\find_wm.ps1"], capture_output=True)

