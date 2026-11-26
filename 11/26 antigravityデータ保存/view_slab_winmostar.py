#!/usr/bin/env python3
"""
Winmostarで今回作成した2H-SiC {10-10}スラブモデル(3x3x2, 72原子)を開くスクリプト
"""
import os
import sys
import shutil
import subprocess

WINMOSTAR_EXE = "/mnt/c/winmos11/winmostar.exe"
WIN_USER_DATA_DIR = "/mnt/c/Users/S015/winmostar_temp"
WIN_USER_DATA_DIR_WIN = r"C:\Users\S015\winmostar_temp"

DEFAULT_CIF = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_10-10_slab_3x3x2_4layers_vacuum.cif"
DEFAULT_XYZ = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_10-10_slab_3x3x2_4layers_vacuum.xyz"
BULK_CIF    = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_10-10_bulk_3x3x2_72atoms.cif"
BULK_XYZ    = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_10-10_bulk_3x3x2_72atoms.xyz"

def open_in_winmostar(file_path):
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return False
        
    os.makedirs(WIN_USER_DATA_DIR, exist_ok=True)
    filename = os.path.basename(file_path)
    target_path = os.path.join(WIN_USER_DATA_DIR, filename)
    shutil.copy2(file_path, target_path)
    
    target_win_path = f"{WIN_USER_DATA_DIR_WIN}\\{filename}"
    print(f"[Winmostar] 起動中: {target_win_path}")
    
    # バックグラウンドで非同期起動
    subprocess.Popen([WINMOSTAR_EXE, target_win_path],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)
    print("✅ Winmostar が正常に起動しました！")
    return True

if __name__ == "__main__":
    target = DEFAULT_CIF
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if "bulk" in arg:
            target = BULK_XYZ if "xyz" in arg else BULK_CIF
        elif "xyz" in arg:
            target = DEFAULT_XYZ
        elif os.path.exists(sys.argv[1]):
            target = os.path.abspath(sys.argv[1])
            
    print(f"表示対象ファイル: {os.path.basename(target)}")
    print("※ 使い方:")
    print("   ・スラブモデル表示: python3 view_slab_winmostar.py")
    print("   ・バルクモデル表示: python3 view_slab_winmostar.py bulk")
    open_in_winmostar(target)
