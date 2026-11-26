import ase.io
from ase.build import make_supercell

# Load the unit cell CIF file
atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif")

# Create a 2x2x1 supercell
atoms_supercell = atoms * (2, 2, 1)

# Save the supercell to a new CIF file
output_path = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_supercell_2x2x1.cif"
ase.io.write(output_path, atoms_supercell)
print(f"Saved supercell to {output_path}")
