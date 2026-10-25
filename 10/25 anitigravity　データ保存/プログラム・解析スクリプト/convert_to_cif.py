import ase.io

# Load the xyz we just created
atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon_frame.xyz")

# Set a dummy unit cell to ensure CIF is written correctly without error
# A large enough box so atoms are not cut off
atoms.cell = [20, 20, 20]
atoms.center()

output_cif = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon_frame.cif"
ase.io.write(output_cif, atoms)
print("Saved to", output_cif)
