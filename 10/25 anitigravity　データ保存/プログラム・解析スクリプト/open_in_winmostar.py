import sys
import os
import shutil
import subprocess

# Path to Winmostar executable in Windows
WINMOSTAR_EXE = "/mnt/c/winmos11/winmostar.exe"
# Windows local directory for reliable loading without UNC path issues
WIN_USER_DATA_DIR = "/mnt/c/Users/S015/winmostar_temp"
WIN_USER_DATA_DIR_WIN = r"C:\Users\S015\winmostar_temp"

CUT_PLANES_DIR = "/home/yamazaki/mdi_workspace_backup/research_simulations/cut_planes"

AVAILABLE_FILES = {
    "1": ("2H-SiC_hex_cluster_cut_10-10_m-plane.cif", "{10-10} m-plane 切断クラスタ (CIF)"),
    "2": ("2H-SiC_hex_cluster_cut_11-20_a-plane.cif", "{11-20} a-plane 切断クラスタ (CIF)"),
    "3": ("2H-SiC_hex_cluster_cut_10-11.cif",          "{10-11} 半極性面 切断クラスタ (CIF)"),
    "4": ("2H-SiC_hex_cluster_cut_11-22.cif",          "{11-22} 半極性面 切断クラスタ (CIF)"),
    "5": ("2H-SiC_10-10_m-plane_slab.cif",            "{10-10} m-plane 表面スラブ (CIF)"),
    "6": ("2H-SiC_11-20_a-plane_slab.cif",            "{11-20} a-plane 表面スラブ (CIF)"),
    "7": ("2H-SiC_10-11_pyramidal_slab.cif",          "{10-11} 半極性面 表面スラブ (CIF)"),
    "8": ("2H-SiC_11-22_pyramidal_slab.cif",          "{11-22} 半極性面 表面スラブ (CIF)"),
    "9": ("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_10-10_slab_3x3x2_4layers_vacuum.cif", "{10-10} 3x3x2 表面スラブ (4層/72原子/真空10Å) (CIF)"),
    "10": ("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_10-10_bulk_3x3x2_72atoms.cif",        "{10-10} 3x3x2 バルク参照モデル (4層/72原子/真空なし) (CIF)"),
}

def open_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
        
    os.makedirs(WIN_USER_DATA_DIR, exist_ok=True)
    filename = os.path.basename(file_path)
    target_path = os.path.join(WIN_USER_DATA_DIR, filename)
    shutil.copy2(file_path, target_path)
    
    # Windows native path
    target_win_path = f"{WIN_USER_DATA_DIR_WIN}\\{filename}"
    print(f"Opening in Winmostar: {target_win_path}")
    
    # Launch Winmostar asynchronously in background
    subprocess.Popen([WINMOSTAR_EXE, target_win_path],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)
    print("Winmostar launched successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target in AVAILABLE_FILES:
            fname = AVAILABLE_FILES[target][0]
            filepath = fname if os.path.isabs(fname) else os.path.join(CUT_PLANES_DIR, fname)
            open_file(filepath)
        elif os.path.exists(target):
            open_file(os.path.abspath(target))
        else:
            # Match by keyword
            matched = [fname for num, (fname, desc) in AVAILABLE_FILES.items() if target.lower() in fname.lower() or target.lower() in desc.lower()]
            if matched:
                open_file(os.path.join(CUT_PLANES_DIR, matched[0]))
            else:
                print(f"Unknown file or option: {target}")
    else:
        print("=== Winmostar 切断面ファイル一覧 ===")
        for key, (fname, desc) in AVAILABLE_FILES.items():
            print(f" [{key}] {desc}")
        print("\n使い方例: python3 open_in_winmostar.py 1")
        print("         python3 open_in_winmostar.py 5")
