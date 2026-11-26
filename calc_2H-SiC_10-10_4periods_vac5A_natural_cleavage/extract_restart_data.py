#!/usr/bin/env python3
import os

def create_restart_data():
    base_dir = "/home/yamazaki/mdi_workspace_backup/calc_2H-SiC_10-10_4periods_vac5A_natural_cleavage"
    orig_data = os.path.join(base_dir, "slab_10-10_144atoms.data")
    dump_file = os.path.join(base_dir, "dump.lammpstrj")
    out_data = os.path.join(base_dir, "slab_10-10_144atoms_restart.data")

    # 1. Parse last frame of dump
    with open(dump_file, 'r') as fin:
        lines = fin.readlines()

    i = 0
    frames = []
    while i < len(lines):
        line = lines[i].strip()
        if line == 'ITEM: TIMESTEP':
            step = int(lines[i+1].strip())
            i += 2
        elif line == 'ITEM: NUMBER OF ATOMS':
            natoms = int(lines[i+1].strip())
            i += 2
        elif line.startswith('ITEM: BOX BOUNDS'):
            i += 4
        elif line.startswith('ITEM: ATOMS'):
            cols = line.split()[2:]
            id_idx = cols.index('id')
            x_idx = cols.index('x')
            y_idx = cols.index('y')
            z_idx = cols.index('z')
            atoms = {}
            for _ in range(natoms):
                i += 1
                parts = lines[i].split()
                aid = int(parts[id_idx])
                x = float(parts[x_idx])
                y = float(parts[y_idx])
                z = float(parts[z_idx])
                atoms[aid] = (x, y, z)
            frames.append((step, atoms))
            i += 1
        else:
            i += 1

    last_step, last_coords = frames[-1]
    print(f"Extracted {len(frames)} frames. Using frame at timestep {last_step}.")

    # 2. Read original data and replace coordinates
    with open(orig_data, 'r') as fin:
        orig_lines = fin.readlines()

    with open(out_data, 'w') as fout:
        in_atoms = False
        for line in orig_lines:
            if 'Atoms' in line:
                in_atoms = True
                fout.write(line)
                continue
            if in_atoms:
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0].isdigit():
                    aid = int(parts[0])
                    atype = parts[1]
                    if aid in last_coords:
                        x, y, z = last_coords[aid]
                        fout.write(f" {aid:5d} {atype:3s} {x:18.14f} {y:18.14f} {z:18.14f}\n")
                    else:
                        fout.write(line)
                else:
                    if len(parts) == 0 and in_atoms:
                        # End of atoms or separator
                        pass
                    fout.write(line)
            else:
                fout.write(line)

    print(f"Successfully generated restart data: {out_data}")

if __name__ == "__main__":
    create_restart_data()
