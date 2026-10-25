import os
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data
import matplotlib.pyplot as plt

def build_10_10_slab_3x3x2():
    # 1. 2H-SiC CIFファイルの読み込み
    cif_input = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif"
    out_dir = "/home/yamazaki/mdi_workspace_backup/research_simulations"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Loading 2H-SiC crystal from {cif_input}...")
    bulk = ase.io.read(cif_input)
    
    # 2. {10-10} 面スラブの構築 (layers=2: 1周期2層なので合計4層)
    # indices=(1, 0, 0) は六方晶の (1 0 -1 0) 面に対応
    slab_unit = surface(bulk, indices=(1, 0, 0), layers=2, vacuum=None)
    
    # 3. 3x3x1 スーパーセルの作成 (面内 3x3、z方向は2周期4層のまま維持)
    slab_3x3 = slab_unit * (3, 3, 1)
    
    # 4. z方向の座標調整と真空層の追加 (上下に各10Å)
    pos = slab_3x3.positions
    z_min = np.min(pos[:, 2])
    z_max = np.max(pos[:, 2])
    thickness = z_max - z_min
    
    # 最下層の原子が z = 10.0 Å になるようにシフト
    pos[:, 2] = pos[:, 2] - z_min + 10.0
    slab_3x3.positions = pos
    
    # セルの z 軸長さを (厚み + 20.0 Å) に設定 (下端に10Å、上端に10Åの真空)
    cell = slab_3x3.cell.copy()
    cell[2, 2] = thickness + 20.0
    slab_3x3.cell = cell
    slab_3x3.pbc = [True, True, True]
    
    # x, y をセル内に収める
    slab_3x3.wrap()
    
    # 各層の z 座標を確認
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 3))
    n_si = sum(s == 'Si' for s in slab_3x3.get_chemical_symbols())
    n_c = sum(s == 'C' for s in slab_3x3.get_chemical_symbols())
    
    print(f"\n==========================================")
    print(f"3x3x2 Slab Model generated successfully:")
    print(f"  - Total Atoms: {len(slab_3x3)} (Si: {n_si}, C: {n_c})")
    print(f"  - Cell dimensions: a={slab_3x3.cell[0,0]:.4f} Å, b={slab_3x3.cell[1,1]:.4f} Å, c={slab_3x3.cell[2,2]:.4f} Å")
    print(f"  - Cell angles: alpha={slab_3x3.cell.angles()[0]:.1f}°, beta={slab_3x3.cell.angles()[1]:.1f}°, gamma={slab_3x3.cell.angles()[2]:.1f}°")
    print(f"  - Atomic layers (z levels): {z_unique} Å")
    for idx, z_val in enumerate(z_unique, 1):
        count = sum(np.isclose(slab_3x3.positions[:, 2], z_val, atol=0.01))
        print(f"      Layer {idx}: z={z_val:.3f} Å ({count} atoms)")
    print(f"  - Bottom vacuum: {np.min(slab_3x3.positions[:, 2]):.4f} Å (Target: 10.0 Å)")
    print(f"  - Top vacuum: {slab_3x3.cell[2,2] - np.max(slab_3x3.positions[:, 2]):.4f} Å (Target: 10.0 Å)")
    print(f"==========================================\n")
    
    # 5. ファイル保存 (3x3x2 モデル)
    base_prefix = os.path.join(out_dir, "2H-SiC_10-10_slab_3x3x2_4layers_vacuum")
    ase.io.write(f"{base_prefix}.cif", slab_3x3)
    ase.io.write(f"{base_prefix}.xyz", slab_3x3)
    write_lammps_data(f"{base_prefix}.data", slab_3x3, atom_style='atomic', masses=True)
    print(f"Saved 3x3x2 slab files to:\n  - {base_prefix}.cif\n  - {base_prefix}.xyz\n  - {base_prefix}.data")
    
    # 6. 構造の断面図プロット作成
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    
    pos = slab_3x3.positions
    syms = slab_3x3.get_chemical_symbols()
    colors = {'Si': '#1f77b4', 'C': '#ff7f0e'}
    sizes = {'Si': 150, 'C': 80}
    cell = slab_3x3.cell
    
    # (a) x-z 断面図
    ax1 = axes[0]
    for s in ['Si', 'C']:
        mask = [sym == s for sym in syms]
        ax1.scatter(pos[mask, 0], pos[mask, 2], c=colors[s], s=sizes[s], label=s, edgecolors='black', zorder=3)
    ax1.plot([0, cell[0,0], cell[0,0], 0, 0], [0, 0, cell[2,2], cell[2,2], 0], 'k--', label='Periodic Cell')
    ax1.axhline(10.0, color='r', linestyle=':', label='Bottom Fracture Surface (z=10Å)')
    ax1.axhline(10.0 + thickness, color='r', linestyle=':', label=f'Top Fracture Surface (z={10.0+thickness:.2f}Å)')
    ax1.set_xlim(-1, cell[0,0] + 1)
    ax1.set_ylim(-1, cell[2,2] + 1)
    ax1.set_xlabel('x [Å] ([11-20] direction, 3x size)')
    ax1.set_ylabel('z [Å] (Cleavage normal {10-10})')
    ax1.set_title('Side View (x-z plane, 3x3x2 model, 72 atoms)\nShowing 4 layers & 10Å Vacuums', fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # (b) y-z 断面図
    ax2 = axes[1]
    for s in ['Si', 'C']:
        mask = [sym == s for sym in syms]
        ax2.scatter(pos[mask, 1], pos[mask, 2], c=colors[s], s=sizes[s], label=s, edgecolors='black', zorder=3)
    ax2.plot([0, cell[1,1], cell[1,1], 0, 0], [0, 0, cell[2,2], cell[2,2], 0], 'k--', label='Periodic Cell')
    ax2.axhline(10.0, color='r', linestyle=':', label='Bottom Fracture Surface (z=10Å)')
    ax2.axhline(10.0 + thickness, color='r', linestyle=':', label=f'Top Fracture Surface (z={10.0+thickness:.2f}Å)')
    ax2.set_xlim(-1, cell[1,1] + 1)
    ax2.set_ylim(-1, cell[2,2] + 1)
    ax2.set_xlabel('y [Å] (c-axis [0001] direction, 3x size)')
    ax2.set_ylabel('z [Å] (Cleavage normal {10-10})')
    ax2.set_title('Side View (y-z plane, 3x3x2 model, 72 atoms)\nShowing 4 layers & 10Å Vacuums', fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plot_path = os.path.join(out_dir, "2H-SiC_10-10_slab_3x3x2_structure.png")
    plt.savefig(plot_path, dpi=200)
    print(f"Saved structure plot to {plot_path}")

if __name__ == "__main__":
    build_10_10_slab_3x3x2()
