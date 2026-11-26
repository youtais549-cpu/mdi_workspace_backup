#!/usr/bin/env python3
"""
create_restart_structure.py
dump.lammpstrj の最終フレームから、次回計算再開用の LAMMPS データファイル
(slab_10-10_144atoms_restart.data) および可視化用 CIF/XYZ を生成するスクリプト。
"""

import sys
import os
import numpy as np

def extract_latest_frame(dump_path, out_data_path, out_xyz_path=None):
    if not os.path.exists(dump_path):
        print(f"Error: {dump_path} not found.")
        sys.exit(1)

    with open(dump_path, 'r') as f:
        lines = f.readlines()

    # TIMESTEP の位置を検索
    step_indices = [i for i, line in enumerate(lines) if line.startswith("ITEM: TIMESTEP")]
    if not step_indices:
        print("Error: No TIMESTEP found in dump file.")
        sys.exit(1)

    last_step_idx = step_indices[-1]
    timestep = int(lines[last_step_idx + 1].strip())
    natoms = int(lines[last_step_idx + 3].strip())
    
    # Box bounds
    x_bounds = [float(v) for v in lines[last_step_idx + 5].split()]
    y_bounds = [float(v) for v in lines[last_step_idx + 6].split()]
    z_bounds = [float(v) for v in lines[last_step_idx + 7].split()]

    # Atoms: ITEM: ATOMS id type x y z
    atom_lines = lines[last_step_idx + 9 : last_step_idx + 9 + natoms]
    atoms = []
    for line in atom_lines:
        parts = line.split()
        if len(parts) >= 5:
            aid = int(parts[0])
            atype = int(parts[1])
            x = float(parts[2])
            y = float(parts[3])
            z = float(parts[4])
            atoms.append((aid, atype, x, y, z))

    # 原子 ID でソート
    atoms.sort(key=lambda a: a[0])

    print(f"✅ Extracted Timestep {timestep} with {len(atoms)} atoms.")
    print(f"   Box: X [{x_bounds[0]:.4f}, {x_bounds[1]:.4f}], Y [{y_bounds[0]:.4f}, {y_bounds[1]:.4f}], Z [{z_bounds[0]:.4f}, {z_bounds[1]:.4f}]")

    # LAMMPS data ファイル書き出し
    with open(out_data_path, 'w') as f:
        f.write(f"# LAMMPS data file - Restart from Timestep {timestep} (4-period 144-atom 2H-SiC)\n\n")
        f.write(f"{len(atoms)} atoms\n")
        f.write("2 atom types\n\n")
        f.write(f"{x_bounds[0]:.16e} {x_bounds[1]:.16e} xlo xhi\n")
        f.write(f"{y_bounds[0]:.16e} {y_bounds[1]:.16e} ylo yhi\n")
        f.write(f"{z_bounds[0]:.16e} {z_bounds[1]:.16e} zlo zhi\n\n")
        f.write("Masses\n\n")
        f.write("1 12.011  # C\n")
        f.write("2 28.085  # Si\n\n")
        f.write("Atoms # atomic\n\n")
        for aid, atype, x, y, z in atoms:
            f.write(f"{aid} {atype} {x:.8f} {y:.8f} {z:.8f}\n")

    print(f"✅ LAMMPS restart data written: {out_data_path}")

    # XYZ 書き出し (Winmostar用)
    if out_xyz_path:
        type_to_elem = {1: 'C', 2: 'Si'}
        with open(out_xyz_path, 'w') as f:
            f.write(f"{len(atoms)}\n")
            f.write(f"Restart structure from Timestep {timestep} (4 periods, vac 5A)\n")
            for aid, atype, x, y, z in atoms:
                elem = type_to_elem.get(atype, 'X')
                f.write(f"{elem} {x:.8f} {y:.8f} {z:.8f}\n")
        print(f"✅ XYZ structure written: {out_xyz_path}")

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    dump_file = os.path.join(work_dir, "dump.lammpstrj")
    out_data = os.path.join(work_dir, "slab_10-10_144atoms_restart.data")
    out_xyz = os.path.join(work_dir, "latest_structure.xyz")
    extract_latest_frame(dump_file, out_data, out_xyz)
