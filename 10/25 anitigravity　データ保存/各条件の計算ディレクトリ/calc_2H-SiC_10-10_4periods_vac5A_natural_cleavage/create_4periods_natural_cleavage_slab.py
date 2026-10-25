#!/usr/bin/env python3
import os
import json
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data

def build_4periods_natural_cleavage_slab():
    out_dir = "/home/yamazaki/mdi_workspace_backup/calc_2H-SiC_10-10_4periods_vac5A_natural_cleavage"
    os.makedirs(out_dir, exist_ok=True)
    cif_input = "/home/yamazaki/mdi_workspace_backup/research_simulations/2H-SiC.cif"
    
    print(f"Loading 2H-SiC crystal from {cif_input}...")
    bulk_cif = ase.io.read(cif_input)
    
    # 2. {10-10} 面スラブの構築 (layers=4: 1周期2層なので合計8層, 4周期)
    # 2周期モデル (create_10-10_slab_3x3x2.py) と全く同一の自然へき開面 (粗結合 1.78Å 切断)
    slab_unit = surface(bulk_cif, indices=(1, 0, 0), layers=4, vacuum=None)
    
    # 3. 3x3x1 スーパーセル (面内 3x3, 144原子)
    slab_3x3 = slab_unit * (3, 3, 1)
    
    # 4. z方向の座標調整と真空層の追加 (上下に各 5.0 Å, 合計 10.0 Å)
    pos = slab_3x3.positions.copy()
    z_min = float(np.min(pos[:, 2]))
    z_max = float(np.max(pos[:, 2]))
    thickness = z_max - z_min
    
    # 最下層の原子が z = 5.0 Å になるようにシフト
    pos[:, 2] = pos[:, 2] - z_min + 5.0
    slab_3x3.positions = pos
    
    # セルの z 軸長さを (厚み + 10.0 Å) に設定 (下端に5Å、上端に5Åの真空)
    cell = slab_3x3.cell.copy()
    cell[2, 2] = thickness + 10.0
    slab_3x3.cell = cell
    slab_3x3.pbc = [True, True, True]
    slab_3x3.wrap()
    
    # 層間距離と原子数の確認
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 3))
    diffs = [round(z_unique[i+1] - z_unique[i], 3) for i in range(len(z_unique)-1)]
    n_si = sum(s == 'Si' for s in slab_3x3.get_chemical_symbols())
    n_c = sum(s == 'C' for s in slab_3x3.get_chemical_symbols())
    
    print(f"\n==========================================")
    print(f"4-Periods Natural Cleavage Slab Model Generated:")
    print(f"  - Total Atoms: {len(slab_3x3)} (Si: {n_si}, C: {n_c})")
    print(f"  - Cell: Lx={slab_3x3.cell[0,0]:.4f} Å, Ly={slab_3x3.cell[1,1]:.4f} Å, Lz={slab_3x3.cell[2,2]:.4f} Å")
    print(f"  - Thickness: {thickness:.4f} Å")
    print(f"  - Atomic Layers ({len(z_unique)} layers): {z_unique} Å")
    print(f"  - Interlayer Spacings: {diffs} Å")
    print(f"  - Bottom vacuum: {np.min(slab_3x3.positions[:, 2]):.4f} Å (Target: 5.0 Å)")
    print(f"  - Top vacuum: {slab_3x3.cell[2,2] - np.max(slab_3x3.positions[:, 2]):.4f} Å (Target: 5.0 Å)")
    
    syms = np.array(slab_3x3.get_chemical_symbols())
    mask_b = np.isclose(slab_3x3.positions[:, 2], z_unique[0], atol=0.01)
    mask_t = np.isclose(slab_3x3.positions[:, 2], z_unique[-1], atol=0.01)
    print(f"  - Bottom layer: {sum(mask_b)} atoms (C: {sum(syms[mask_b]=='C')}, Si: {sum(syms[mask_b]=='Si')}) [Nonpolar]")
    print(f"  - Top layer:    {sum(mask_t)} atoms (C: {sum(syms[mask_t]=='C')}, Si: {sum(syms[mask_t]=='Si')}) [Nonpolar]")
    print(f"==========================================\n")
    
    # 5. スラブファイル保存
    prefix_slab = os.path.join(out_dir, "slab_10-10_144atoms")
    ase.io.write(f"{prefix_slab}.cif", slab_3x3)
    ase.io.write(f"{prefix_slab}.xyz", slab_3x3)
    write_lammps_data(f"{prefix_slab}.data", slab_3x3, atom_style='atomic', masses=True)
    
    # 6. バルクモデルの構築 (真空 0 Å, 真の結晶格子長 10.6556 Å)
    bulk_pos = slab_3x3.positions.copy()
    bulk_pos[:, 2] = bulk_pos[:, 2] - 5.0 # シフト戻し (0.0 からスタート)
    bulk_cell = slab_3x3.cell.copy()
    # 粗結合 1.7758 Å を足したものが真の周期長
    bulk_cell[2, 2] = thickness + (diffs[1]) # 8.8798 + 1.7758 = 10.6556 Å
    bulk_atoms = ase.Atoms(symbols=slab_3x3.get_chemical_symbols(), positions=bulk_pos, cell=bulk_cell, pbc=[True, True, True])
    bulk_atoms.wrap()
    
    prefix_bulk = os.path.join(out_dir, "bulk_10-10_144atoms")
    ase.io.write(f"{prefix_bulk}.cif", bulk_atoms)
    ase.io.write(f"{prefix_bulk}.xyz", bulk_atoms)
    write_lammps_data(f"{prefix_bulk}.data", bulk_atoms, atom_style='atomic', masses=True)
    
    # 7. メタデータ JSON 出力
    area_A = float(slab_3x3.cell[0,0] * slab_3x3.cell[1,1])
    area_2A = 2.0 * area_A
    conv_factor = 16.021766
    
    meta = {
        'cleavage_plane': '10-10',
        'cleavage_type': 'natural_cleavage_sparse_bond',
        'n_periods': 4,
        'n_layers': 8,
        'natoms': len(slab_3x3),
        'vacuum_thickness_angstrom': 5.0,
        'supercell_xy': [3, 3],
        'cell_slab': [float(slab_3x3.cell[0,0]), float(slab_3x3.cell[1,1]), float(slab_3x3.cell[2,2])],
        'cell_bulk': [float(bulk_atoms.cell[0,0]), float(bulk_atoms.cell[1,1]), float(bulk_atoms.cell[2,2])],
        'area_A_angstrom2': area_A,
        'total_area_2A_angstrom2': area_2A,
        'unit_conversion_eV_A2_to_J_m2': conv_factor,
        'effective_denominator': float(area_2A / conv_factor),
        'true_bulk_scf_energy_eV': -63863.3059,
        'true_bulk_scf_energy_Ry': -4693.86470519,
        'slab_data_file': "slab_10-10_144atoms.data",
        'bulk_data_file': "bulk_10-10_144atoms.data"
    }
    with open(os.path.join(out_dir, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
        
    print(f"Saved all 4-period natural cleavage files to {out_dir}")

if __name__ == "__main__":
    build_4periods_natural_cleavage_slab()
