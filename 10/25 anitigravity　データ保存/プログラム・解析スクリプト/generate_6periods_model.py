#!/usr/bin/env python3
"""
generate_6periods_model.py
6周期 (12層, 216原子) 2H-SiC {10-10} スラブモデルおよびバルクモデル生成スクリプト
"""

import os
import sys
import json
import numpy as np
from ase import Atoms
import ase.io
from ase.io.lammpsdata import write_lammps_data

# 基本物性パラメータ
LATTICE_A = 3.076
LATTICE_C = 5.048
N_PERIODS = 6
SUPERCELL_XY = (3, 3)
VACUUM = 5.0

def build_2h_sic_10_10_6periods():
    a = LATTICE_A
    c = LATTICE_C
    nx, ny = SUPERCELL_XY
    
    d_10_10 = np.sqrt(3) * a
    dense_dz = d_10_10 / 6.0    # ~0.888 Å
    sparse_dz = d_10_10 / 3.0   # ~1.776 Å
    
    unit_positions = []
    unit_symbols = []
    
    for p in range(N_PERIODS):
        base_z = p * (dense_dz + sparse_dz)
        # Layer 1
        z1 = base_z + dense_dz
        unit_positions.append([0.0, 0.0, z1])
        unit_symbols.append('Si')
        unit_positions.append([0.5 * a, 0.5 * c, z1])
        unit_symbols.append('C')
        
        # Layer 2
        z2 = z1 + sparse_dz
        unit_positions.append([0.5 * a, 0.0, z2])
        unit_symbols.append('Si')
        unit_positions.append([0.0, 0.5 * c, z2])
        unit_symbols.append('C')
        
    unit_positions = np.array(unit_positions)
    slab_thickness = unit_positions[:, 2].max() - unit_positions[:, 2].min()
    
    # 1. スラブモデル
    cell_slab = [a * nx, c * ny, slab_thickness + 2.0 * VACUUM]
    pos_slab = []
    sym_slab = []
    
    for ix in range(nx):
        for iy in range(ny):
            for i in range(len(unit_positions)):
                x = (unit_positions[i, 0] + ix * a) % cell_slab[0]
                y = (unit_positions[i, 1] + iy * c) % cell_slab[1]
                z = unit_positions[i, 2] - unit_positions[:, 2].min() + VACUUM
                pos_slab.append([x, y, z])
                sym_slab.append(unit_symbols[i])
                
    slab_atoms = Atoms(symbols=sym_slab, positions=pos_slab, cell=cell_slab, pbc=[True, True, True])
    
    # 2. バルク基準モデル
    cell_bulk = [a * nx, c * ny, N_PERIODS * d_10_10]
    pos_bulk = []
    sym_bulk = []
    for ix in range(nx):
        for iy in range(ny):
            for i in range(len(unit_positions)):
                x = (unit_positions[i, 0] + ix * a) % cell_bulk[0]
                y = (unit_positions[i, 1] + iy * c) % cell_bulk[1]
                z = unit_positions[i, 2] % cell_bulk[2]
                pos_bulk.append([x, y, z])
                sym_bulk.append(unit_symbols[i])
                
    bulk_atoms = Atoms(symbols=sym_bulk, positions=pos_bulk, cell=cell_bulk, pbc=[True, True, True])
    area_A = (a * nx) * (c * ny)
    
    return slab_atoms, bulk_atoms, area_A

def main():
    out_dir = "/home/yamazaki/mdi_workspace_backup/calc_2H-SiC_10-10_6periods_vac5A"
    os.makedirs(out_dir, exist_ok=True)
    
    slab, bulk, area_A = build_2h_sic_10_10_6periods()
    n_atoms = len(slab)
    area_2A = 2.0 * area_A
    conv_factor = 16.021766
    
    print(f"6周期モデル生成:")
    print(f"  総原子数: {n_atoms} 原子 (Si: {n_atoms//2}, C: {n_atoms//2})")
    print(f"  スラブ寸法: {slab.cell[0,0]:.4f} x {slab.cell[1,1]:.4f} x {slab.cell[2,2]:.4f} Å")
    print(f"  バルク寸法: {bulk.cell[0,0]:.4f} x {bulk.cell[1,1]:.4f} x {bulk.cell[2,2]:.4f} Å")
    print(f"  破面積 2A : {area_2A:.4f} Å²")
    
    # ファイル書き出し
    slab_data = os.path.join(out_dir, "slab_10-10_216atoms.data")
    bulk_data = os.path.join(out_dir, "bulk_10-10_216atoms.data")
    write_lammps_data(slab_data, slab, atom_style='atomic', masses=True)
    write_lammps_data(bulk_data, bulk, atom_style='atomic', masses=True)
    ase.io.write(os.path.join(out_dir, "slab_10-10_216atoms.xyz"), slab)
    ase.io.write(os.path.join(out_dir, "slab_10-10_216atoms.cif"), slab)
    
    # メタデータ
    meta = {
        'cleavage_plane': '10-10',
        'n_periods': N_PERIODS,
        'n_layers': N_PERIODS * 2,
        'natoms': n_atoms,
        'vacuum_thickness_angstrom': VACUUM,
        'supercell_xy': list(SUPERCELL_XY),
        'cell_slab': [float(slab.cell[0,0]), float(slab.cell[1,1]), float(slab.cell[2,2])],
        'cell_bulk': [float(bulk.cell[0,0]), float(bulk.cell[1,1]), float(bulk.cell[2,2])],
        'area_A_angstrom2': float(area_A),
        'total_area_2A_angstrom2': float(area_2A),
        'unit_conversion_eV_A2_to_J_m2': conv_factor,
        'effective_denominator': float(area_2A / conv_factor),
        'slab_data_file': "slab_10-10_216atoms.data",
        'bulk_data_file': "bulk_10-10_216atoms.data"
    }
    with open(os.path.join(out_dir, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
        
    print(f"✅ 生成完了: {out_dir}")

if __name__ == "__main__":
    main()
