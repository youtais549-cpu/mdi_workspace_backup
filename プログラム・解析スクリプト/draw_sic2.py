import ase.io
from ase.visualize.plot import plot_atoms
import matplotlib.pyplot as plt

# Load the CIF file
atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif")
atoms_supercell = atoms * (2, 2, 1)

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
plot_atoms(atoms, axes[0], radii=0.5, rotation=('15x,45y,0z'))
axes[0].set_title('Unit Cell (2H-SiC)')
axes[0].axis('off')

plot_atoms(atoms_supercell, axes[1], radii=0.5, rotation=('15x,45y,0z'))
axes[1].set_title('2x2x1 Supercell')
axes[1].axis('off')

fig.savefig("/home/yamazaki/.gemini/antigravity-ide/brain/80099415-a731-4ba2-8db5-552b3ade134a/2H_SiC_hexagonal_schematic.png", dpi=300, bbox_inches='tight')
