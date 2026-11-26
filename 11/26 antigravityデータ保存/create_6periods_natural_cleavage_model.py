#!/usr/bin/env python3
import os
import json
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data

def build_6periods_natural_cleavage_models():
    base_dir = "/home/yamazaki/mdi_workspace_backup"
    cif_input = os.path.join(base_dir, "research_simulations/2H-SiC.cif")
    
    dir_slab = os.path.join(base_dir, "calc_2H-SiC_10-10_6periods_vac5A_natural_cleavage")
    dir_bulk = os.path.join(base_dir, "calc_2H-SiC_10-10_6periods_true_bulk_scf")
    os.makedirs(dir_slab, exist_ok=True)
    os.makedirs(dir_bulk, exist_ok=True)
    
    print(f"Loading 2H-SiC crystal from {cif_input}...")
    bulk_cif = ase.io.read(cif_input)
    
    # 1. 6周期 {10-10} 面スラブの構築 (layers=6: 6周期 12層)
    # 2周期・4周期と完全に同一の ASE surface ロジック (粗結合 1.776Å 切断, 密結合ペア保持)
    slab_unit = surface(bulk_cif, indices=(1, 0, 0), layers=6, vacuum=None)
    slab_3x3 = slab_unit * (3, 3, 1)
    
    pos = slab_3x3.positions.copy()
    z_min = float(np.min(pos[:, 2]))
    z_max = float(np.max(pos[:, 2]))
    thickness = z_max - z_min
    
    # 最下層を z = 5.0 Å にシフト
    pos[:, 2] = pos[:, 2] - z_min + 5.0
    slab_3x3.positions = pos
    
    # セル Z 軸長 = 厚み + 10.0 Å (真空 下5Å + 上5Å)
    cell = slab_3x3.cell.copy()
    cell[2, 2] = thickness + 10.0
    slab_3x3.cell = cell
    slab_3x3.pbc = [True, True, True]
    slab_3x3.wrap()
    
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 3))
    diffs = [round(z_unique[i+1] - z_unique[i], 3) for i in range(len(z_unique)-1)]
    n_si = sum(s == 'Si' for s in slab_3x3.get_chemical_symbols())
    n_c = sum(s == 'C' for s in slab_3x3.get_chemical_symbols())
    
    print(f"\n==========================================")
    print(f"6-Periods Natural Cleavage Slab Model Generated:")
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
    
    # 2. 6周期真のバルクモデルの構築 (真空 0 Å, 完全周期的結晶)
    bulk_pos = slab_3x3.positions.copy()
    bulk_pos[:, 2] = bulk_pos[:, 2] - 5.0 # シフト戻し (0.0 からスタート)
    bulk_cell = slab_3x3.cell.copy()
    # 粗結合 1.7760 Å を足したものが真の周期長
    bulk_cell[2, 2] = thickness + diffs[1] # 14.2076 + 1.7760 = 15.9836 Å
    bulk_atoms = ase.Atoms(symbols=slab_3x3.get_chemical_symbols(), positions=bulk_pos, cell=bulk_cell, pbc=[True, True, True])
    bulk_atoms.wrap()
    
    z_b_unique = np.unique(np.round(bulk_atoms.positions[:, 2], 3))
    diffs_b = [round(z_b_unique[i+1] - z_b_unique[i], 3) for i in range(len(z_b_unique)-1)]
    boundary_spacing = round(bulk_cell[2, 2] - z_b_unique[-1] + z_b_unique[0], 3)
    
    print(f"==========================================")
    print(f"6-Periods True Bulk Model Generated:")
    print(f"  - Total Atoms: {len(bulk_atoms)} (Si: {n_si}, C: {n_c})")
    print(f"  - Bulk Cell: Lx={bulk_atoms.cell[0,0]:.4f} Å, Ly={bulk_atoms.cell[1,1]:.4f} Å, Lz={bulk_atoms.cell[2,2]:.4f} Å")
    print(f"  - Bulk Spacings: {diffs_b} Å")
    print(f"  - Periodic boundary spacing across cell: {boundary_spacing:.4f} Å (Target: 1.776 Å)")
    print(f"==========================================\n")
    
    # 3. ファイル保存 (スラブ用)
    prefix_slab = os.path.join(dir_slab, "slab_10-10_216atoms")
    ase.io.write(f"{prefix_slab}.cif", slab_3x3)
    ase.io.write(f"{prefix_slab}.xyz", slab_3x3)
    write_lammps_data(f"{prefix_slab}.data", slab_3x3, atom_style='atomic', masses=True)
    
    # バルク用もスラブディレクトリ内に配置
    prefix_bulk_in_slab = os.path.join(dir_slab, "bulk_10-10_216atoms")
    ase.io.write(f"{prefix_bulk_in_slab}.cif", bulk_atoms)
    ase.io.write(f"{prefix_bulk_in_slab}.xyz", bulk_atoms)
    write_lammps_data(f"{prefix_bulk_in_slab}.data", bulk_atoms, atom_style='atomic', masses=True)
    
    # 4. ファイル保存 (バルク専用ディレクトリ)
    prefix_bulk_only = os.path.join(dir_bulk, "bulk_10-10_216atoms_true_bulk")
    ase.io.write(f"{prefix_bulk_only}.cif", bulk_atoms)
    ase.io.write(f"{prefix_bulk_only}.xyz", bulk_atoms)
    write_lammps_data(f"{prefix_bulk_only}.data", bulk_atoms, atom_style='atomic', masses=True)
    
    # 5. メタデータ JSON 出力
    area_A = float(slab_3x3.cell[0,0] * slab_3x3.cell[1,1])
    area_2A = 2.0 * area_A
    conv_factor = 16.021766
    
    meta = {
        'cleavage_plane': '10-10',
        'cleavage_type': 'natural_cleavage_sparse_bond',
        'n_periods': 6,
        'n_layers': 12,
        'natoms': len(slab_3x3),
        'vacuum_thickness_angstrom': 5.0,
        'supercell_xy': [3, 3],
        'cell_slab': [float(slab_3x3.cell[0,0]), float(slab_3x3.cell[1,1]), float(slab_3x3.cell[2,2])],
        'cell_bulk': [float(bulk_atoms.cell[0,0]), float(bulk_atoms.cell[1,1]), float(bulk_atoms.cell[2,2])],
        'area_A_angstrom2': area_A,
        'total_area_2A_angstrom2': area_2A,
        'unit_conversion_eV_A2_to_J_m2': conv_factor,
        'effective_denominator': float(area_2A / conv_factor),
        'slab_data_file': "slab_10-10_216atoms.data",
        'bulk_data_file': "bulk_10-10_216atoms.data"
    }
    with open(os.path.join(dir_slab, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
    with open(os.path.join(dir_bulk, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
        
    print(f"Successfully generated 6-period slab and bulk files!")

if __name__ == "__main__":
    build_6periods_natural_cleavage_models()
