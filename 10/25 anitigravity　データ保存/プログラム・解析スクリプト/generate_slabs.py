import ase.io
from ase.build import surface
import matplotlib.pyplot as plt
from ase.visualize.plot import plot_atoms
import os

atoms = ase.io.read("/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif")
out_dir = "/home/yamazaki/mdi_workspace_backup/research_simulations/cut_planes"
os.makedirs(out_dir, exist_ok=True)

planes = [
    ("10-10_m-plane", (1, 0, 0), r"$\{10\bar{1}0\}$ (m-plane)"),
    ("11-20_a-plane", (1, 1, 0), r"$\{11\bar{2}0\}$ (a-plane)"),
    ("10-11_pyramidal", (1, 0, 1), r"$\{10\bar{1}1\}$"),
    ("11-22_pyramidal", (1, 1, 2), r"$\{11\bar{2}2\}$")
]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, (name, indices, label) in enumerate(planes):
    slab = surface(atoms, indices=indices, layers=4, vacuum=8.0)
    # Clear tags and spacegroup info for plotting
    slab.set_tags(None)
    slab.info = {}
    
    # Save CIF and XYZ
    cif_path = os.path.join(out_dir, f"2H-SiC_{name}_slab.cif")
    xyz_path = os.path.join(out_dir, f"2H-SiC_{name}_slab.xyz")
    ase.io.write(cif_path, slab)
    ase.io.write(xyz_path, slab)
    
    # Repeat for nice visualization
    slab_rep = slab * (2, 2, 1)
    slab_rep.set_tags(None)
    slab_rep.info = {}
    
    ax = axes[idx]
    plot_atoms(slab_rep, ax, radii=0.5, rotation=('20x,35y,0z'))
    ax.set_title(f"{label} Surface Slab", fontsize=13, fontweight='bold')
    ax.axis('off')

plt.tight_layout()
slab_fig = "/home/yamazaki/.gemini/antigravity-ide/brain/8a08be02-065e-4160-ac56-fb5df11bb973/slabs_overview.png"
plt.savefig(slab_fig, dpi=200)
print("Saved slabs overview image to", slab_fig)
