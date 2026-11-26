import ase.io
from ase import Atoms
import numpy as np

# Load the original unit cell
atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif")
cell = atoms.cell

all_symbols = []
all_positions = []

frac_coords = atoms.get_scaled_positions()
symbols = atoms.get_chemical_symbols()

# 1. Original cell
for sym, fc in zip(symbols, frac_coords):
    all_symbols.append(sym)
    cart = cell.cartesian_positions(fc)
    all_positions.append(cart)

# 2. Rotated 120 degrees
for sym, fc in zip(symbols, frac_coords):
    x, y, z = fc
    new_fc = np.array([-y, x - y, z])
    all_symbols.append(sym)
    cart = cell.cartesian_positions(new_fc)
    all_positions.append(cart)

# 3. Rotated 240 degrees
for sym, fc in zip(symbols, frac_coords):
    x, y, z = fc
    new_fc = np.array([y - x, -x, z])
    all_symbols.append(sym)
    cart = cell.cartesian_positions(new_fc)
    all_positions.append(cart)

# Add dummy atoms (He) at the 12 vertices of the hexagonal prism
# The 6 vertices in the basal plane (fractional coords of the primitive cell basis):
# a1, a1+a2, a2, -a1, -a1-a2, -a2
hex_vertices_frac = [
    np.array([1, 0, 0]),
    np.array([1, 1, 0]),
    np.array([0, 1, 0]),
    np.array([-1, 0, 0]),
    np.array([-1, -1, 0]),
    np.array([0, -1, 0])
]

# Add bottom (z=0) and top (z=1) vertices
dummy_element = 'He'
for z in [0, 1]:
    for v_frac in hex_vertices_frac:
        v = np.copy(v_frac)
        v[2] = z
        cart = cell.cartesian_positions(v)
        all_symbols.append(dummy_element)
        all_positions.append(cart)

# Also add a dummy atom at the center (origin) to help visual structure if needed,
# but we will just add the vertices.

hexagon_cluster = Atoms(symbols=all_symbols, positions=all_positions)
hexagon_cluster.center(vacuum=5.0)

# Save as XYZ
output_xyz = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon_frame.xyz"
ase.io.write(output_xyz, hexagon_cluster)
print("Saved hexagon with frame to", output_xyz)
