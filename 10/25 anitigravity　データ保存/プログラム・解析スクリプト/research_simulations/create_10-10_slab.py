import os
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data
import matplotlib.pyplot as plt
from ase.visualize.plot import plot_atoms

def build_10_10_slab():
    # 1. 2H-SiC CIFファイルの読み込み
    cif_input = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif"
    out_dir = "/home/yamazaki/mdi_workspace_backup/research_simulations"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Loading 2H-SiC crystal from {cif_input}...")
    bulk = ase.io.read(cif_input)
    
    # 2. {10-10} 面スラブの構築 (layers=2: 1周期2層なので合計4層)
    # indices=(1, 0, 0) は六方晶の (1 0 -1 0) 面に対応
    # layers=2 で 2周期 (4層) を生成
    slab = surface(bulk, indices=(1, 0, 0), layers=2, vacuum=None)
    
    # 3. z方向の座標調整と真空層の追加 (上下に各10Å)
    pos = slab.positions
    z_min = np.min(pos[:, 2])
    z_max = np.max(pos[:, 2])
    thickness = z_max - z_min
    
    # 最下層の原子が z = 10.0 Å になるようにシフト
    pos[:, 2] = pos[:, 2] - z_min + 10.0
    slab.positions = pos
    
    # セルの z 軸長さを (厚み + 20.0 Å) に設定 (下端に10Å、上端に10Åの真空)
    cell = slab.cell.copy()
    cell[2, 2] = thickness + 20.0
    slab.cell = cell
    slab.pbc = [True, True, True]
    
    # x, y をセル内に収める (境界付近の微小誤差をラップ)
    slab.wrap()
    
    # 各層の z 座標を確認
    z_unique = np.unique(np.round(slab.positions[:, 2], 3))
    print(f"Slab generated successfully:")
    print(f"  - Number of atoms: {len(slab)} (Si: {sum(s=='Si' for s in slab.get_chemical_symbols())}, C: {sum(s=='C' for s in slab.get_chemical_symbols())})")
    print(f"  - Cell dimensions: a={slab.cell[0,0]:.4f} Å, b={slab.cell[1,1]:.4f} Å, c={slab.cell[2,2]:.4f} Å")
    print(f"  - Cell angles: alpha={slab.cell.angles()[0]:.1f}°, beta={slab.cell.angles()[1]:.1f}°, gamma={slab.cell.angles()[2]:.1f}°")
    print(f"  - Atomic layers (z levels): {z_unique} Å")
    print(f"  - Bottom vacuum: {np.min(slab.positions[:, 2]):.4f} Å (Target: 10.0 Å)")
    print(f"  - Top vacuum: {slab.cell[2,2] - np.max(slab.positions[:, 2]):.4f} Å (Target: 10.0 Å)")
    
    # 4. 基本セル (1x1) の保存
    base_prefix = os.path.join(out_dir, "2H-SiC_10-10_slab_4layers_vacuum")
    ase.io.write(f"{base_prefix}.cif", slab)
    ase.io.write(f"{base_prefix}.xyz", slab)
    write_lammps_data(f"{base_prefix}.data", slab, atom_style='atomic', masses=True)
    print(f"Saved 1x1 slab files to {base_prefix}.[cif|xyz|data]")
    
    # 5. 2x2 スーパーセル版 (32原子) の作成と保存
    slab_2x2 = slab * (2, 2, 1)
    slab_2x2.pbc = [True, True, True]
    prefix_2x2 = os.path.join(out_dir, "2H-SiC_10-10_slab_4layers_vacuum_2x2")
    ase.io.write(f"{prefix_2x2}.cif", slab_2x2)
    ase.io.write(f"{prefix_2x2}.xyz", slab_2x2)
    write_lammps_data(f"{prefix_2x2}.data", slab_2x2, atom_style='atomic', masses=True)
    print(f"Saved 2x2 slab files to {prefix_2x2}.[cif|xyz|data]")
    
    # 6. 構造の可視化プロット生成
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    
    # 視覚的に分かりやすいように 3x3 繰り返しで側面図・上面図をプロット
    slab_rep = slab * (3, 3, 1)
    slab_rep.set_tags(None)
    slab_rep.info = {}
    
    # (a) 側面図 (yz平面: 水平y, 垂直z)
    ax = axes[0]
    plot_atoms(slab_rep, ax, radii=0.6, rotation=('0x,90y,0z'))
    ax.set_title("Side View (along x-axis, y-z plane)\nShowing 4 layers & Vacuums", fontsize=11, fontweight='bold')
    ax.set_xlabel("y [Å]")
    ax.set_ylabel("z [Å]")
    ax.axhline(10.0, color='r', linestyle='--', alpha=0.5, label='Bottom surface (z=10Å)')
    ax.axhline(10.0 + thickness, color='r', linestyle='--', alpha=0.5, label=f'Top surface (z={10.0+thickness:.2f}Å)')
    ax.legend(loc='upper right', fontsize=8)
    
    # (b) 側面図 (xz平面: 水平x, 垂直z)
    ax = axes[1]
    plot_atoms(slab_rep, ax, radii=0.6, rotation=('0x,0y,0z'))
    ax.set_title("Side View (along y-axis, x-z plane)", fontsize=11, fontweight='bold')
    ax.set_xlabel("x [Å]")
    ax.set_ylabel("z [Å]")
    ax.axhline(10.0, color='r', linestyle='--', alpha=0.5)
    ax.axhline(10.0 + thickness, color='r', linestyle='--', alpha=0.5)
    
    # (c) 斜視図 (3D perspective)
    ax = axes[2]
    plot_atoms(slab_rep, ax, radii=0.6, rotation=('15x,30y,0z'))
    ax.set_title("{10-10} Cleavage Surface (4 layers)\nwith 10Å Vacuums", fontsize=11, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plot_path = os.path.join(out_dir, "2H-SiC_10-10_slab_structure.png")
    plt.savefig(plot_path, dpi=200)
    print(f"Saved structure plot to {plot_path}")

if __name__ == "__main__":
    build_10_10_slab()
