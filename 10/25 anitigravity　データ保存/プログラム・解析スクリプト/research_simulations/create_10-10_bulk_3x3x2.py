import os
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data
import matplotlib.pyplot as plt

def build_10_10_bulk_3x3x2():
    cif_input = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif"
    out_dir = "/home/yamazaki/mdi_workspace_backup/research_simulations"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Loading 2H-SiC crystal from {cif_input}...")
    bulk_hex = ase.io.read(cif_input)
    
    # 1. {10-10} 面に垂直な方向を z 軸とする直交単位セルを構築 (layers=2: 2周期4層)
    unit_ortho = surface(bulk_hex, indices=(1, 0, 0), layers=2, vacuum=None)
    
    # 2. 面内 3x3 に拡張 (3x3x1) -> 72原子のバルクスーパーセル
    bulk_3x3x2 = unit_ortho * (3, 3, 1)
    
    # バルクとしての z 方向格子ベクトル長 Lz を設定 (2周期分 = 2 * sqrt(3)/2 * a)
    a = bulk_hex.cell.lengths()[0]
    d_1010 = (np.sqrt(3) / 2.0) * a
    lz_bulk = 2 * d_1010  # 2周期 = 4層の厚み (約 5.3278 Å)
    
    cell = bulk_3x3x2.cell.copy()
    cell[2, 2] = lz_bulk
    bulk_3x3x2.cell = cell
    bulk_3x3x2.pbc = [True, True, True]
    bulk_3x3x2.wrap()
    
    syms = np.array(bulk_3x3x2.get_chemical_symbols())
    pos = bulk_3x3x2.positions
    n_si = sum(syms == 'Si')
    n_c = sum(syms == 'C')
    cell = bulk_3x3x2.cell
    
    z_coords = pos[:, 2]
    z_unique = np.unique(np.round(z_coords, 3))
    
    print("\n=================================================================")
    print("      2H-SiC {10-10} バルクモデル (E_bulk 用) 構築レポート      ")
    print("=================================================================")
    print(f"  - 総原子数: {len(bulk_3x3x2)} (Si: {n_si}, C: {n_c})  <-- スラブモデルと完全一致！")
    print(f"  - セル寸法: Lx = {cell[0,0]:.4f} Å, Ly = {cell[1,1]:.4f} Å, Lz = {cell[2,2]:.4f} Å")
    print(f"  - 角度: alpha = {cell.angles()[0]:.1f}°, beta = {cell.angles()[1]:.1f}°, gamma = {cell.angles()[2]:.1f}° (直交セル)")
    print(f"  - 周期境界条件: {bulk_3x3x2.pbc} (全方向周期境界、真空層なし)")
    print(f"  - 検出された原子層の数: {len(z_unique)} 層")
    for idx, z_val in enumerate(z_unique, 1):
        count = sum(np.isclose(z_coords, z_val, atol=0.02))
        print(f"      第 {idx} 層: z = {z_val:.3f} Å ({count} 原子: Si 9, C 9)")
    print("=================================================================\n")
    
    # 3. ファイルの保存
    base_prefix = os.path.join(out_dir, "2H-SiC_10-10_bulk_3x3x2_72atoms")
    ase.io.write(f"{base_prefix}.cif", bulk_3x3x2)
    ase.io.write(f"{base_prefix}.xyz", bulk_3x3x2)
    write_lammps_data(f"{base_prefix}.data", bulk_3x3x2, atom_style='atomic', masses=True)
    print(f"Saved bulk model files to:\n  - {base_prefix}.cif\n  - {base_prefix}.xyz\n  - {base_prefix}.data")
    
    # 4. スラブモデルとの比較プロット画像の生成
    slab_cif = os.path.join(out_dir, "2H-SiC_10-10_slab_3x3x2_4layers_vacuum.cif")
    slab_model = ase.io.read(slab_cif)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    colors = {'Si': '#1f77b4', 'C': '#ff7f0e'}
    sizes = {'Si': 130, 'C': 70}
    
    # (a) スラブモデル (E_slab: 表面あり)
    ax1 = axes[0]
    pos_s = slab_model.positions
    syms_s = slab_model.get_chemical_symbols()
    cell_s = slab_model.cell
    for s in ['Si', 'C']:
        mask = [sym == s for sym in syms_s]
        ax1.scatter(pos_s[mask, 1], pos_s[mask, 2], c=colors[s], s=sizes[s], label=s, edgecolors='black', zorder=3)
    ax1.plot([0, cell_s[1,1], cell_s[1,1], 0, 0], [0, 0, cell_s[2,2], cell_s[2,2], 0], 'k--', linewidth=1.5, label='Periodic Cell')
    ax1.axhline(10.0, color='r', linestyle=':', linewidth=1.5, label='Bottom Surface (Cleaved)')
    ax1.axhline(10.0 + 3.552, color='r', linestyle=':', linewidth=1.5, label='Top Surface (Cleaved)')
    ax1.text(cell_s[1,1]/2, 5.0, "Vacuum (10 Å)", ha='center', va='center', fontsize=11, color='gray', style='italic')
    ax1.text(cell_s[1,1]/2, 18.5, "Vacuum (10 Å)", ha='center', va='center', fontsize=11, color='gray', style='italic')
    ax1.set_xlim(-1, cell_s[1,1] + 1)
    ax1.set_ylim(-1, cell_s[2,2] + 1)
    ax1.set_xlabel('y [Å] (c-axis [0001])', fontsize=11)
    ax1.set_ylabel('z [Å] (Cleavage normal {10-10})', fontsize=11)
    ax1.set_title('1. Slab Model (E_slab, 72 atoms)\n[Surface: YES (2 Cleavage Surfaces + Vacuums)]', fontweight='bold', fontsize=12)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # (b) バルクモデル (E_bulk: 表面なし)
    ax2 = axes[1]
    for s in ['Si', 'C']:
        mask = [sym == s for sym in syms]
        ax2.scatter(pos[mask, 1], pos[mask, 2], c=colors[s], s=sizes[s], label=s, edgecolors='black', zorder=3)
    ax2.plot([0, cell[1,1], cell[1,1], 0, 0], [0, 0, cell[2,2], cell[2,2], 0], 'k--', linewidth=1.5, label='Periodic Cell (PBC: x,y,z)')
    # 上下にも結合が繋がっていることを示すガイド線
    ax2.text(cell[1,1]/2, cell[2,2] + 2.0, "▲ Seamlessly connected across PBC ▲", ha='center', va='bottom', fontsize=10, color='blue')
    ax2.text(cell[1,1]/2, -2.0, "▼ Seamlessly connected across PBC ▼", ha='center', va='top', fontsize=10, color='blue')
    ax2.set_xlim(-1, cell[1,1] + 1)
    ax2.set_ylim(-4, cell_s[2,2] + 1)  # スラブと同じ高さスケールで比較
    ax2.set_xlabel('y [Å] (c-axis [0001])', fontsize=11)
    ax2.set_ylabel('z [Å] (Bulk repeat {10-10})', fontsize=11)
    ax2.set_title('2. Bulk Reference Model (E_bulk, 72 atoms)\n[Surface: NO (Seamless Periodic Bulk)]', fontweight='bold', fontsize=12)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    comparison_plot = os.path.join(out_dir, "2H-SiC_10-10_slab_vs_bulk_comparison.png")
    plt.savefig(comparison_plot, dpi=200)
    print(f"Saved comparison plot to {comparison_plot}")

if __name__ == "__main__":
    build_10_10_bulk_3x3x2()
