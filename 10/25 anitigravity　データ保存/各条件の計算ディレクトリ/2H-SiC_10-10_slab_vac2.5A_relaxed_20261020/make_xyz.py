import sys
import os

def dump_to_xyz(dump_file, xyz_file):
    if not os.path.exists(dump_file):
        print(f"Error: {dump_file} not found")
        return

    type_to_elem = {1: 'C', 2: 'Si'}

    with open(dump_file, 'r') as fin, open(xyz_file, 'w') as fout:
        lines = fin.readlines()
        i = 0
        n_frames = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == "ITEM: TIMESTEP":
                step = lines[i+1].strip()
                i += 2
            elif line == "ITEM: NUMBER OF ATOMS":
                natoms = int(lines[i+1].strip())
                i += 2
            elif line.startswith("ITEM: BOX BOUNDS"):
                i += 4
            elif line.startswith("ITEM: ATOMS"):
                cols = line.split()[2:]
                id_idx = cols.index("id")
                type_idx = cols.index("type")
                x_idx = cols.index("x")
                y_idx = cols.index("y")
                z_idx = cols.index("z")

                atoms_data = []
                for _ in range(natoms):
                    i += 1
                    parts = lines[i].split()
                    aid = int(parts[id_idx])
                    atype = int(parts[type_idx])
                    x = float(parts[x_idx])
                    y = float(parts[y_idx])
                    z = float(parts[z_idx])
                    elem = type_to_elem.get(atype, 'X')
                    atoms_data.append((aid, elem, x, y, z))

                atoms_data.sort(key=lambda a: a[0])

                fout.write(f"{natoms}\n")
                fout.write(f"Lattice=\"\" Properties=species:S:1:pos:R:3 Time={step}\n")
                for a in atoms_data:
                    fout.write(f"{a[1]:2s} {a[2]:12.6f} {a[3]:12.6f} {a[4]:12.6f}\n")
                n_frames += 1
                i += 1
            else:
                i += 1
    print(f"Converted {n_frames} frames to {xyz_file}")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "dump.lammpstrj"
    dst = sys.argv[2] if len(sys.argv) > 2 else "md_animation.xyz"
    dump_to_xyz(src, dst)
