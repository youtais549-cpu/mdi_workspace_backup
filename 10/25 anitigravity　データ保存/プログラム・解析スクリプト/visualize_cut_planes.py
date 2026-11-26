import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import ase.io
from ase import Atoms

# 1. Load hexagon cluster
atoms_hex = ase.io.read('/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC_hexagon.cif')
positions = atoms_hex.positions.copy()
# Shift center of mass to origin for easy geometric cutting
com = np.mean(positions, axis=0)
pos_centered = positions - com
symbols = atoms_hex.get_chemical_symbols()

# 2. Get bulk lattice cell and reciprocal vectors
atoms_bulk = ase.io.read('/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif')
b_mat = atoms_bulk.cell.reciprocal()

planes = [
    (r"$\{10\bar{1}0\}$ (m-plane)", [1, 0, 0], 'red'),
    (r"$\{11\bar{2}0\}$ (a-plane)", [1, 1, 0], 'blue'),
    (r"$\{10\bar{1}1\}$", [1, 0, 1], 'green'),
    (r"$\{11\bar{2}2\}$", [1, 1, 2], 'purple')
]

fig = plt.figure(figsize=(18, 10))

for idx, (pname, hkl, pcolor) in enumerate(planes, 1):
    ax = fig.add_subplot(2, 2, idx, projection='3d')
    
    # Plane normal
    K = hkl[0] * b_mat[0] + hkl[1] * b_mat[1] + hkl[2] * b_mat[2]
    n = K / np.linalg.norm(K)
    
    # Plot atoms
    # Si: beige (#e4bc84 / tan), C: green (#4a7c59 / forestgreen)
    for pos, sym in zip(pos_centered, symbols):
        color = '#e4a663' if sym == 'Si' else '#5a8268'
        size = 180 if sym == 'Si' else 120
        ax.scatter([pos[0]], [pos[1]], [pos[2]], color=color, s=size, edgecolors='k', linewidth=0.5, alpha=0.95)
    
    # Draw bonds (cutoff 2.1 A)
    for i in range(len(pos_centered)):
        for j in range(i + 1, len(pos_centered)):
            d = np.linalg.norm(pos_centered[i] - pos_centered[j])
            if 1.6 < d < 2.05:
                ax.plot([pos_centered[i, 0], pos_centered[j, 0]],
                        [pos_centered[i, 1], pos_centered[j, 1]],
                        [pos_centered[i, 2], pos_centered[j, 2]],
                        color='gray', linewidth=2.5, alpha=0.7)
                
    # Create plane polygon passing through center (offset slightly if desired, or at d=0)
    # Define an orthonormal basis on the plane: u, v perpendicular to n
    if abs(n[0]) > 0.1 or abs(n[1]) > 0.1:
        u = np.array([-n[1], n[0], 0])
    else:
        u = np.array([1, 0, 0])
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    
    # Plane quad at origin d=0
    L = 2.8
    plane_corners = np.array([
        - L * u - L * v,
          L * u - L * v,
          L * u + L * v,
        - L * u + L * v
    ])
    
    poly = Poly3DCollection([plane_corners], alpha=0.35, facecolor=pcolor, edgecolor=pcolor, linewidth=2)
    ax.add_collection3d(poly)
    
    # Arrow for normal vector
    ax.quiver(0, 0, 0, n[0]*1.8, n[1]*1.8, n[2]*1.8, color=pcolor, linewidth=2, arrow_length_ratio=0.2)
    
    ax.set_title(f"{pname}\nNormal: ({n[0]:.2f}, {n[1]:.2f}, {n[2]:.2f})", fontsize=12, fontweight='bold')
    ax.set_xlim([-3.2, 3.2])
    ax.set_ylim([-3.2, 3.2])
    ax.set_zlim([-3.2, 3.2])
    ax.set_xlabel("X (Å)")
    ax.set_ylabel("Y (Å)")
    ax.set_zlabel("Z (Å, c-axis)")
    ax.view_init(elev=22, azim=45)

plt.tight_layout()
out_png = '/home/yamazaki/.gemini/antigravity-ide/brain/8a08be02-065e-4160-ac56-fb5df11bb973/cut_planes_overview.png'
plt.savefig(out_png, dpi=200)
print("Saved to", out_png)
