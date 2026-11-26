#!/usr/bin/env python3
"""
スラブモデルおよびバルクモデル自動生成ツール
【ユーザー実行コマンド】
python3 generate_models.py

model_settings.py と dft_settings.py を読み込み、
任意の結晶面・周期数・真空層厚さに応じたスラブ・バルクモデル構造ファイル(.data, .cif, .xyz)
および表面積評価メタデータを自動生成します。
"""
import os
import sys
import json
import numpy as np
from ase import Atoms
import ase.io
from ase.io.lammpsdata import write_lammps_data

# 設定ファイルの読み込み
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import model_settings as ms
import dft_settings as ds

def build_2h_sic_10_10(n_periods, supercell_xy, vacuum):
    """
    2H-SiC {10-10} 非極性 m面のスラブおよびバルクモデルを生成
    """
    a = ms.LATTICE_A
    c = ms.LATTICE_C
    u = ms.U_PARAM
    nx, ny = supercell_xy
    
    # {10-10} 面に垂直な方向の1周期厚さ d_{10-10} = sqrt(3)*a/2 * 2 = sqrt(3)*a
    d_10_10 = np.sqrt(3) * a
    
    # 直交基本セル (1周期 = 2層, 4原子: 2 Si, 2 C)
    # x: [11-20], y: [0001] (c軸), z: [10-10] (へき開面法線)
    # 粗結合面 (dz = 1.776Å) で切断し、上面・下面を完全等価(非極性)にする
    dense_dz = d_10_10 / 6.0    # ~0.888 Å
    sparse_dz = d_10_10 / 3.0   # ~1.776 Å
    
    unit_positions = []
    unit_symbols = []
    
    # 周期数 n_periods 分だけ z 方向に積層
    for p in range(n_periods):
        base_z = p * (dense_dz + sparse_dz)
        # Layer 1 (z = base_z + dense_dz)
        z1 = base_z + dense_dz
        unit_positions.append([0.0, 0.0, z1])
        unit_symbols.append('Si')
        unit_positions.append([0.5 * a, 0.5 * c, z1])
        unit_symbols.append('C')
        
        # Layer 2 (z = base_z + dense_dz + sparse_dz)
        z2 = z1 + sparse_dz
        unit_positions.append([0.5 * a, 0.0, z2])
        unit_symbols.append('Si')
        unit_positions.append([0.0, 0.5 * c, z2])
        unit_symbols.append('C')
        
    unit_positions = np.array(unit_positions)
    slab_thickness = unit_positions[:, 2].max() - unit_positions[:, 2].min()
    
    # --- 1. スラブモデルの構築 (真空層あり) ---
    cell_slab = [a * nx, c * ny, slab_thickness + 2.0 * vacuum]
    pos_slab = []
    sym_slab = []
    
    for ix in range(nx):
        for iy in range(ny):
            for i in range(len(unit_positions)):
                x = (unit_positions[i, 0] + ix * a) % cell_slab[0]
                y = (unit_positions[i, 1] + iy * c) % cell_slab[1]
                z = unit_positions[i, 2] - unit_positions[:, 2].min() + vacuum
                pos_slab.append([x, y, z])
                sym_slab.append(unit_symbols[i])
                
    slab_atoms = Atoms(symbols=sym_slab, positions=pos_slab, cell=cell_slab, pbc=[True, True, True])
    
    # --- 2. バルク基準モデルの構築 (真空層なし, 同一原子数) ---
    cell_bulk = [a * nx, c * ny, n_periods * d_10_10]
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
    
    # 破面断面積 A の算出
    area_A = (a * nx) * (c * ny)
    
    return slab_atoms, bulk_atoms, area_A

def main():
    print("==================================================")
    print(" 表面破壊エネルギー用 モデル自動生成ツール")
    print("==================================================")
    print(f"結晶面: {ms.CLEAVAGE_PLANE}")
    print(f"周期数: {ms.N_PERIODS} 周期 ({ms.N_PERIODS * 2} 層)")
    print(f"面内サイズ: {ms.SUPERCELL_XY[0]} x {ms.SUPERCELL_XY[1]}")
    print(f"真空層厚さ: {ms.VACUUM_THICKNESS} Å (上下各 {ms.VACUUM_THICKNESS} Å)")
    
    if ms.CLEAVAGE_PLANE == '10-10':
        slab, bulk, area_A = build_2h_sic_10_10(ms.N_PERIODS, ms.SUPERCELL_XY, ms.VACUUM_THICKNESS)
    else:
        raise NotImplementedError(f"結晶面 '{ms.CLEAVAGE_PLANE}' のジェネレーターは準備中です。'10-10' を指定してください。")
        
    n_atoms = len(slab)
    area_2A = 2.0 * area_A
    conv_factor = 16.021766
    
    print("--------------------------------------------------")
    print(f"総原子数 (スラブ & バルク共通): {n_atoms} 原子")
    print(f"スラブセル寸法: Lx={slab.cell[0,0]:.4f}Å, Ly={slab.cell[1,1]:.4f}Å, Lz={slab.cell[2,2]:.4f}Å")
    print(f"バルクセル寸法: Lx={bulk.cell[0,0]:.4f}Å, Ly={bulk.cell[1,1]:.4f}Å, Lz={bulk.cell[2,2]:.4f}Å")
    print(f"破面断面積 A   : {area_A:.4f} Å²")
    print(f"全破面表面積 2A: {area_2A:.4f} Å²")
    print(f"換算式: γ [J/m²] = (E_slab - E_bulk) / {area_2A:.4f} * {conv_factor:.6f}")
    print(f"                 = ΔE / {area_2A / conv_factor:.4f}")
    print("--------------------------------------------------")
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    prefix_slab = os.path.join(out_dir, f"slab_{ms.CLEAVAGE_PLANE}_{n_atoms}atoms")
    prefix_bulk = os.path.join(out_dir, f"bulk_{ms.CLEAVAGE_PLANE}_{n_atoms}atoms")
    
    # スラブファイルの出力
    ase.io.write(f"{prefix_slab}.cif", slab)
    ase.io.write(f"{prefix_slab}.xyz", slab)
    write_lammps_data(f"{prefix_slab}.data", slab, atom_style='atomic', masses=True)
    
    # バルクファイルの出力
    ase.io.write(f"{prefix_bulk}.cif", bulk)
    ase.io.write(f"{prefix_bulk}.xyz", bulk)
    write_lammps_data(f"{prefix_bulk}.data", bulk, atom_style='atomic', masses=True)
    
    # メタデータ JSON の出力 (calc_surface_energy.py で自動参照)
    meta = {
        'cleavage_plane': ms.CLEAVAGE_PLANE,
        'n_periods': ms.N_PERIODS,
        'n_layers': ms.N_PERIODS * 2,
        'natoms': n_atoms,
        'vacuum_thickness_angstrom': ms.VACUUM_THICKNESS,
        'supercell_xy': list(ms.SUPERCELL_XY),
        'cell_slab': [float(slab.cell[0,0]), float(slab.cell[1,1]), float(slab.cell[2,2])],
        'cell_bulk': [float(bulk.cell[0,0]), float(bulk.cell[1,1]), float(bulk.cell[2,2])],
        'area_A_angstrom2': float(area_A),
        'total_area_2A_angstrom2': float(area_2A),
        'unit_conversion_eV_A2_to_J_m2': conv_factor,
        'effective_denominator': float(area_2A / conv_factor),
        'slab_data_file': os.path.basename(f"{prefix_slab}.data"),
        'bulk_data_file': os.path.basename(f"{prefix_bulk}.data")
    }
    meta_path = os.path.join(out_dir, "fracture_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
        
    print(f"✅ モデルファイルおよびメタデータを生成しました:")
    print(f"  - スラブ: {os.path.basename(prefix_slab)}.[data|cif|xyz]")
    print(f"  - バルク: {os.path.basename(prefix_bulk)}.[data|cif|xyz]")
    print(f"  - メタデータ: fracture_metadata.json")

if __name__ == "__main__":
    main()
