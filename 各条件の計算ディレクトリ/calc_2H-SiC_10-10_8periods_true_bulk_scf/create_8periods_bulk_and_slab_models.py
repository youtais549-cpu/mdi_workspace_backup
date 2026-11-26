#!/usr/bin/env python3
"""
create_8periods_bulk_and_slab_models.py
2H-SiC {10-10} 8周期 (16層, 288原子) 真のバルク基準モデル & 自然へき開スラブモデル (真空 5.0 Å) 生成スクリプト
【準拠ルール】
- AGENTS.md §1: スラブ緩和前の「同一原子数 (288原子) 真のバルクモデル (真空 0 Å) 1点SCF先行確定」
- AGENTS.md §2: Type 1 = C (12.011), Type 2 = Si (28.085)
- AGENTS.md §10: ASE surface(bulk, indices=(1, 0, 0), layers=8) による統一生成 (粗結合 1.776 Å 切断)
"""
import os
import json
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data


def build_8periods_models():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(out_dir)
    cif_input = os.path.join(workspace_dir, "research_simulations", "2H-SiC.cif")

    print(f"Loading 2H-SiC unit cell from {cif_input}...")
    bulk_cif = ase.io.read(cif_input)

    # 1. {10-10} 面 8周期モデルの構築 (layers=8 -> 1周期2層なので合計16層)
    slab_unit = surface(bulk_cif, indices=(1, 0, 0), layers=8, vacuum=None)

    # 2. 面内 3x3 スーパーセル拡張 (合計 288 原子: Si 144, C 144)
    slab_3x3 = slab_unit * (3, 3, 1)

    # 3. スラブモデル座標調整 (上下に各 5.0 Å、合計 10.0 Å の真空層)
    pos = slab_3x3.positions.copy()
    z_min = float(np.min(pos[:, 2]))
    z_max = float(np.max(pos[:, 2]))
    thickness = z_max - z_min

    pos[:, 2] = pos[:, 2] - z_min + 5.0
    slab_3x3.positions = pos

    cell_slab = slab_3x3.cell.copy()
    cell_slab[2, 2] = thickness + 10.0
    slab_3x3.cell = cell_slab
    slab_3x3.pbc = [True, True, True]
    slab_3x3.wrap()

    # 層間距離プロファイルの検証
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 4))
    diffs = [round(float(z_unique[i + 1] - z_unique[i]), 4) for i in range(len(z_unique) - 1)]
    n_si = sum(s == 'Si' for s in slab_3x3.get_chemical_symbols())
    n_c = sum(s == 'C' for s in slab_3x3.get_chemical_symbols())

    # 4. 真のバルク基準モデル (真空 0 Å, 周期境界で粗結合 1.7757518 Å が繋がる真の結晶格子長)
    # 1周期長 d_{10-10} = (sqrt(3)/2) * a = 2.6638941420409297 Å -> 8周期 = 21.311153136327437 Å
    bulk_pos = slab_3x3.positions.copy()
    bulk_pos[:, 2] = bulk_pos[:, 2] - 5.0  # z = 0.0 Å から開始
    bulk_cell = slab_3x3.cell.copy()
    exact_d_period = (np.sqrt(3.0) / 2.0) * 3.076
    bulk_cell[2, 2] = 8.0 * exact_d_period
    bulk_atoms = ase.Atoms(
        symbols=slab_3x3.get_chemical_symbols(),
        positions=bulk_pos,
        cell=bulk_cell,
        pbc=[True, True, True],
    )
    bulk_atoms.wrap()

    print("\n============================================================")
    print(" 8-Periods (16 layers, 288 atoms) True Bulk & Slab Models")
    print("============================================================")
    print(f"  - Total Atoms       : {len(bulk_atoms)} (Si: {n_si}, C: {n_c})")
    print(f"  - Bulk Cell (0 Å)   : Lx={bulk_atoms.cell[0,0]:.4f} Å, Ly={bulk_atoms.cell[1,1]:.4f} Å, Lz={bulk_atoms.cell[2,2]:.6f} Å")
    print(f"  - Slab Cell (vac 5Å): Lx={slab_3x3.cell[0,0]:.4f} Å, Ly={slab_3x3.cell[1,1]:.4f} Å, Lz={slab_3x3.cell[2,2]:.6f} Å")
    print(f"  - Number of Layers  : {len(z_unique)} layers")
    print(f"  - Interlayer dz     : {diffs[:4]} ... {diffs[-2:]} Å")
    print(f"    (Both ends dense ~0.8881 Å preserved, outer cleavage sparse ~1.7758 Å)")
    print("============================================================\n")

    # 5. バルク構造ファイルの出力 (.cif, .xyz, .data)
    prefix_bulk = os.path.join(out_dir, "bulk_10-10_288atoms_true_bulk")
    ase.io.write(f"{prefix_bulk}.cif", bulk_atoms)
    ase.io.write(f"{prefix_bulk}.xyz", bulk_atoms)
    write_lammps_data(f"{prefix_bulk}.data", bulk_atoms, atom_style='atomic', masses=True)

    # 6. スラブ構造ファイルの出力 (.cif, .xyz, .data)
    prefix_slab = os.path.join(out_dir, "slab_10-10_288atoms_vac5A")
    ase.io.write(f"{prefix_slab}.cif", slab_3x3)
    ase.io.write(f"{prefix_slab}.xyz", slab_3x3)
    write_lammps_data(f"{prefix_slab}.data", slab_3x3, atom_style='atomic', masses=True)

    # 7. Quantum ESPRESSO 1点SCF入力ファイル (espresso.pwi) の生成
    # 6周期 (calc_2H-SiC_10-10_6periods_true_bulk_scf/espresso.pwi) と完全同一のDFT条件
    pwi_lines = [
        "&CONTROL",
        "   calculation      = 'scf'",
        "   restart_mode     = 'from_scratch'",
        "   tstress          = .true.",
        "   tprnfor          = .true.",
        "   outdir           = './tmp'",
        "   prefix           = 'sic'",
        "   pseudo_dir       = './'",
        "   disk_io          = 'minimal'",
        "/",
        "&SYSTEM",
        "   ibrav            = 0",
        "   ecutwfc          = 40.0",
        "   ecutrho          = 320.0",
        "   occupations      = 'smearing'",
        "   degauss          = 0.01",
        "   smearing         = 'gaussian'",
        "   ntyp             = 2",
        f"   nat              = {len(bulk_atoms)}",
        "/",
        "&ELECTRONS",
        "   electron_maxstep = 200",
        "   conv_thr         = 1e-05",
        "   mixing_mode      = 'local-TF'",
        "   mixing_beta      = 0.3",
        "/",
        "&IONS",
        "/",
        "&CELL",
        "/",
        "&FCP",
        "/",
        "&RISM",
        "/",
        "ATOMIC_SPECIES",
        "Si 28.085 Si.upf",
        "C 12.011 C.upf",
        "",
        "K_POINTS gamma",
        "",
        "CELL_PARAMETERS angstrom",
        f"{bulk_atoms.cell[0,0]:.14f} 0.00000000000000 0.00000000000000",
        f"0.00000000000000 {bulk_atoms.cell[1,1]:.14f} 0.00000000000000",
        f"0.00000000000000 0.00000000000000 {bulk_atoms.cell[2,2]:.14f}",
        "",
        "ATOMIC_POSITIONS angstrom",
    ]
    for sym, p in zip(bulk_atoms.get_chemical_symbols(), bulk_atoms.positions):
        pwi_lines.append(f"{sym} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}")

    pwi_path = os.path.join(out_dir, "espresso.pwi")
    with open(pwi_path, "w", encoding="utf-8") as f:
        f.write("\n".join(pwi_lines) + "\n")

    # 8. メタデータ JSON の保存
    area_A = float(slab_3x3.cell[0, 0] * slab_3x3.cell[1, 1])
    area_2A = 2.0 * area_A
    conv_factor = 16.021766

    meta = {
        "cleavage_plane": "10-10",
        "cleavage_type": "natural_cleavage_sparse_bond",
        "n_periods": 8,
        "n_layers": 16,
        "natoms": len(bulk_atoms),
        "vacuum_thickness_angstrom": 5.0,
        "supercell_xy": [3, 3],
        "cell_slab": [float(slab_3x3.cell[0, 0]), float(slab_3x3.cell[1, 1]), float(slab_3x3.cell[2, 2])],
        "cell_bulk": [float(bulk_atoms.cell[0, 0]), float(bulk_atoms.cell[1, 1]), float(bulk_atoms.cell[2, 2])],
        "area_A_angstrom2": area_A,
        "total_area_2A_angstrom2": area_2A,
        "unit_conversion_eV_A2_to_J_m2": conv_factor,
        "effective_denominator": float(area_2A / conv_factor),
        "expected_bulk_energy_eV_approx": round(-31935.3562 * 4, 4),
        "slab_data_file": "slab_10-10_288atoms_vac5A.data",
        "bulk_data_file": "bulk_10-10_288atoms_true_bulk.data",
    }
    meta_path = os.path.join(out_dir, "fracture_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    print(f"✅ Generated all 8-period (288 atoms) files in {out_dir}")


if __name__ == "__main__":
    build_8periods_models()
