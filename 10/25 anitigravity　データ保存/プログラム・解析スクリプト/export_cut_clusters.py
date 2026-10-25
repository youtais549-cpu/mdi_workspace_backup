import os
import numpy as np
import ase.io
from ase import Atoms

atoms_hex = ase.io.read('/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon.cif')
positions = atoms_hex.positions.copy()
com = np.mean(positions, axis=0)
pos_centered = positions - com
symbols = np.array(atoms_hex.get_chemical_symbols())

atoms_bulk = ase.io.read('/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif')
b_mat = atoms_bulk.cell.reciprocal()

out_dir = "/home/yamazaki/mdi_workspace_backup/research_simulations/cut_planes"
os.makedirs(out_dir, exist_ok=True)

planes = [
    ("10-10_m-plane", [1, 0, 0]),
    ("11-20_a-plane", [1, 1, 0]),
    ("10-11", [1, 0, 1]),
    ("11-22", [1, 1, 2])
]

for name, hkl in planes:
    K = hkl[0] * b_mat[0] + hkl[1] * b_mat[1] + hkl[2] * b_mat[2]
    n = K / np.linalg.norm(K)
    
    dists = np.dot(pos_centered, n)
    # Kept atoms (front side of plane)
    mask = dists >= -0.1
    kept_symbols = symbols[mask]
    kept_pos = positions[mask]
    
    cut_cluster = Atoms(symbols=kept_symbols, positions=kept_pos)
    cut_cluster.cell = [20, 20, 20]
    cut_cluster.center()
    
    cif_file = os.path.join(out_dir, f"2H-SiC_hex_cluster_cut_{name}.cif")
    xyz_file = os.path.join(out_dir, f"2H-SiC_hex_cluster_cut_{name}.xyz")
    ase.io.write(cif_file, cut_cluster)
    ase.io.write(xyz_file, cut_cluster)
    print(f"Exported {cif_file} with {len(cut_cluster)} atoms")

