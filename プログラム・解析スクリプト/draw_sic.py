import ase.io
from ase.visualize.plot import plot_atoms
import matplotlib.pyplot as plt

# Load the CIF file
atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif")

# Make a 2x2x2 supercell for a better look, or just the unit cell
# For a standard hexagonal unit cell diagram, standard unit cell is good.

fig, ax = plt.subplots()
plot_atoms(atoms, ax, radii=0.5, rotation=('15x,45y,0z'))
fig.savefig("/home/yamazaki/.gemini/antigravity-ide/brain/80099415-a731-4ba2-8db5-552b3ade134a/2H_SiC_unit_cell.png")
