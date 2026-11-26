#!/usr/bin/env python3
"""
prepare_true_bulk_144_scf.py
72原子バルクモデル (2H-SiC_10-10_bulk_3x3x2_72atoms.data) を Z方向に2倍スーパーセル化し、
セル Z軸が正しい 10.65557657 Å の「真の 144原子バルクモデル」とその QE GPU 単独SCF計算用ファイルを生成する。
"""
import os
import shutil
import ase.io
from ase.io.lammpsdata import write_lammps_data

ROOT = "/home/yamazaki/mdi_workspace_backup"
WORK_DIR = os.path.join(ROOT, "calc_2H-SiC_10-10_4periods_true_bulk_scf")
os.makedirs(WORK_DIR, exist_ok=True)

# 1. 72原子バルクデータの読み込みと Z方向2倍スーパーセル化
src_72 = os.path.join(ROOT, "2H-SiC_10-10_bulk_scf_20261020", "2H-SiC_10-10_bulk_3x3x2_72atoms.data")
atoms_72 = ase.io.read(src_72, format='lammps-data')
atoms_144 = atoms_72 * (1, 1, 2)

# LAMMPS data 形式で保存 (Type 1 = C, Type 2 = Si)
data_path = os.path.join(WORK_DIR, "bulk_10-10_144atoms_true_bulk.data")
write_lammps_data(data_path, atoms_144, specorder=['C', 'Si'])
print(f"Generated: {data_path} (nat={len(atoms_144)}, cell={atoms_144.cell})")

# 2. espresso.pwi の直接生成 (2H-SiC_10-10_bulk_scf_20261020 と完全に同一のDFT条件)
symbols = atoms_144.get_chemical_symbols()
positions = atoms_144.get_positions()
cell = atoms_144.get_cell()

pwi_path = os.path.join(WORK_DIR, "espresso.pwi")
with open(pwi_path, "w") as f:
    f.write("&CONTROL\n")
    f.write("    calculation = 'scf'\n")
    f.write("    restart_mode = 'from_scratch'\n")
    f.write("    prefix = 'sic'\n")
    f.write("    pseudo_dir = './'\n")
    f.write("    outdir = './tmp'\n")
    f.write("    tprnfor = .true.\n")
    f.write("    tstress = .true.\n")
    f.write("/\n")
    f.write("&SYSTEM\n")
    f.write(f"    ibrav = 0\n")
    f.write(f"    nat = {len(atoms_144)}\n")
    f.write(f"    ntyp = 2\n")
    f.write(f"    ecutwfc = 40.0\n")
    f.write(f"    ecutrho = 320.0\n")
    f.write(f"    occupations = 'smearing'\n")
    f.write(f"    smearing = 'gaussian'\n")
    f.write(f"    degauss = 0.01\n")
    f.write("/\n")
    f.write("&ELECTRONS\n")
    f.write(f"    conv_thr = 1.0d-5\n")
    f.write(f"    mixing_beta = 0.3\n")
    f.write(f"    mixing_mode = 'local-TF'\n")
    f.write(f"    electron_maxstep = 200\n")
    f.write("/\n")
    f.write("ATOMIC_SPECIES\n")
    f.write(" Si  28.08500  Si.upf\n")
    f.write(" C   12.01100  C.upf\n")
    f.write("CELL_PARAMETERS (angstrom)\n")
    for row in cell:
        f.write(f"  {row[0]:16.8f}  {row[1]:16.8f}  {row[2]:16.8f}\n")
    f.write("ATOMIC_POSITIONS (angstrom)\n")
    for sym, pos in zip(symbols, positions):
        f.write(f"{sym:<3}  {pos[0]:16.8f}  {pos[1]:16.8f}  {pos[2]:16.8f}\n")
    f.write("K_POINTS (gamma)\n")

print(f"Generated: {pwi_path}")

# 3. 擬ポテンシャルファイルのコピー
shutil.copy2(os.path.join(ROOT, "calc_2H-SiC_10-10_4periods_vac5A", "C.upf"), WORK_DIR)
shutil.copy2(os.path.join(ROOT, "calc_2H-SiC_10-10_4periods_vac5A", "Si.upf"), WORK_DIR)

# 4. 実行スクリプト run_bulk_gpu.sh の生成
run_sh_path = os.path.join(WORK_DIR, "run_bulk_gpu.sh")
with open(run_sh_path, "w") as f:
    f.write("""#!/bin/bash
set -e
echo "=========================================="
echo " Starting True 144-atoms Bulk SCF Calculation (T4 GPU)"
echo "=========================================="
nvidia-smi

mkdir -p tmp
echo "Running pw.x (GPU)..."
/content/bin/pw.x < espresso.pwi > espresso.pwo 2>&1

echo "=========================================="
echo " True Bulk Calculation Finished!"
echo " Total energy and forces summary:"
grep -E "(!    total energy|Total force)" espresso.pwo || true
echo "=========================================="
""")
os.chmod(run_sh_path, 0o755)
print(f"Generated: {run_sh_path}")
