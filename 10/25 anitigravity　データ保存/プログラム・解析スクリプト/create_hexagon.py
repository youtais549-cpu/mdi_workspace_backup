import ase.io
from ase import Atoms
import numpy as np

# Load the original unit cell
atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif")
cell = atoms.cell

# We will create a cluster (molecule) from 3 unit cells to form a hexagon
all_symbols = []
all_positions = []

frac_coords = atoms.get_scaled_positions()
symbols = atoms.get_chemical_symbols()

# 1. Original cell
for sym, fc in zip(symbols, frac_coords):
    all_symbols.append(sym)
    # Convert back to cartesian for the final object
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

# Create a new Atoms object (cluster, no periodic boundary conditions so we don't draw a weird box)
# We can just put a large orthogonal cell around it
hexagon_cluster = Atoms(symbols=all_symbols, positions=all_positions)
hexagon_cluster.center(vacuum=5.0)

# Save as both CIF and XYZ
output_cif = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon.cif"
output_xyz = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon.xyz"
ase.io.write(output_cif, hexagon_cluster)
ase.io.write(output_xyz, hexagon_cluster)
print("Saved hexagon to", output_cif)
