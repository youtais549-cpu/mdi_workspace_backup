import numpy as np
import ase.io
from ase import Atoms

# 2H-SiC CIF
atoms_bulk = ase.io.read('/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif')
cell = atoms_bulk.cell
a = cell.lengths()[0]
c = cell.lengths()[2]

print(f"Lattice constants: a = {a:.4f} Å, c = {c:.4f} Å")

# Hexagonal reciprocal lattice vectors
# a1 = [a, 0, 0]
# a2 = [-a/2, sqrt(3)/2*a, 0]
# c  = [0, 0, c]
# Reciprocal:
# b1 = 2pi/a * [1, 1/sqrt(3), 0]
# b2 = 2pi/a * [0, 2/sqrt(3), 0]
# b3 = 2pi/c * [0, 0, 1]

# Normal vectors for (hkil):
# (1 0 -1 0) -> (1 0 0): b1 = 2pi/a * [1, 1/sqrt(3), 0] -> unit vector: [sqrt(3)/2, 1/2, 0]
# (1 1 -2 0) -> (1 1 0): b1 + b2 = 2pi/a * [1, sqrt(3), 0] -> unit vector: [1/2, sqrt(3)/2, 0]
# (1 0 -1 1) -> (1 0 1): b1 + b3
# (1 1 -2 2) -> (1 1 2): b1 + b2 + 2*b3

b_mat = cell.reciprocal()
print("Reciprocal cell:\n", b_mat)

planes = {
    "{10-10} (m-plane)": [1, 0, 0],
    "{11-20} (a-plane)": [1, 1, 0],
    "{10-11} (pyramidal)": [1, 0, 1],
    "{11-22} (pyramidal)": [1, 1, 2]
}

for name, hkl in planes.items():
    # K vector in cartesian
    K = hkl[0] * b_mat[0] + hkl[1] * b_mat[1] + hkl[2] * b_mat[2]
    K_norm = K / np.linalg.norm(K)
    # Angle with c-axis ([0, 0, 1])
    angle_c = np.degrees(np.arccos(np.dot(K_norm, [0, 0, 1])))
    print(f"{name}: hkl={hkl}, Normal={np.round(K_norm, 3)}, Angle with c-axis = {angle_c:.2f}°")

