#!/usr/bin/env python3
"""
create_2periods_vac0.5A_model.py
==============================================================================
2H-SiC {10-10} 2周期 (4層, 72原子) 真空層 0.5 Å 自然へき開スラブモデルの初期条件生成コード

【真空層の厚さの設定方法】:
1. ASE surface(bulk_cif, indices=(1, 0, 0), layers=2, vacuum=None) により、
   2周期 (4原子層) の自然へき開スラブ基本セルを生成し、面内 3x3 スーパーセル (72原子) に拡張。
2. スラブの実厚さ thickness = z_max - z_min (= 3.5520 Å) を算出。
3. 指定した真空層厚さ VACUUM_A = 0.5 [Å] に基づき:
   - 最下層原子の z 座標が z = 0.5 Å になるよう全体をシフト:
     pos[:, 2] = pos[:, 2] - z_min + VACUUM_A
   - セル全体の z 軸長 Lz を「スラブ実厚さ + 上下真空層 (2 * VACUUM_A)」に設定:
     cell[2, 2] = thickness + 2.0 * VACUUM_A  (= 3.5520 + 1.0 = 4.5520 Å)
     (下部真空層 0.5 Å + 上部真空層 0.5 Å = 周期境界を跨ぐスラブ間距離 1.0 Å)
==============================================================================
"""
import os
import numpy as np
import ase.io
from ase.build import surface
from ase.io.lammpsdata import write_lammps_data

# --- 初期条件パラメータ設定 ---
N_PERIODS = 2          # 周期数: 2周期 (4原子層, 72原子)
SUPERCELL_XY = (3, 3)  # 面内スーパーセル: 3x3
VACUUM_A = 0.5         # 真空層の厚さ: 0.5 Å (下端 0.5 Å + 上端 0.5 Å, 合計 1.0 Å)


def build_2periods_vac0_5a_slab():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    cif_input = os.path.join(workspace_dir, "research_simulations", "2H-SiC.cif")
    out_dir = os.path.join(workspace_dir, "calc_2H-SiC_10-10_2periods_vac0.5A_rtx5080")
    os.makedirs(out_dir, exist_ok=True)

    # 1. 2H-SiC 結晶構造の読み込みと {10-10} 自然へき開スラブ (2周期=4層) の構築
    bulk_cif = ase.io.read(cif_input)
    slab_unit = surface(bulk_cif, indices=(1, 0, 0), layers=N_PERIODS, vacuum=None)
    slab_3x3 = slab_unit * (SUPERCELL_XY[0], SUPERCELL_XY[1], 1)

    # 2. スラブ実厚さの算出と z 座標・真空層厚さ (0.5 Å) の設定
    pos = slab_3x3.positions.copy()
    z_min = float(np.min(pos[:, 2]))
    z_max = float(np.max(pos[:, 2]))
    thickness = z_max - z_min  # 3.552036 Å

    # 下端に VACUUM_A (0.5 Å) の真空層を配置
    pos[:, 2] = pos[:, 2] - z_min + VACUUM_A
    slab_3x3.positions = pos

    # セル z 軸長 Lz = スラブ実厚さ + 2 * VACUUM_A (下端 0.5 Å + 上端 0.5 Å)
    cell = slab_3x3.cell.copy()
    cell[2, 2] = thickness + 2.0 * VACUUM_A
    slab_3x3.cell = cell
    slab_3x3.pbc = [True, True, True]

    # 3. 層間距離プロファイルの検証 ([0.8881, 1.7758, 0.8881] Å)
    z_unique = np.unique(np.round(slab_3x3.positions[:, 2], 4))
    diffs = [round(float(z_unique[i + 1] - z_unique[i]), 4) for i in range(len(z_unique) - 1)]

    print("============================================================")
    print(f" 2H-SiC {{10-10}} 2周期・真空層 {VACUUM_A} Å スラブ初期構造設定")
    print("============================================================")
    print(f"  - 総原子数        : {len(slab_3x3)} 原子 (Si: 36, C: 36)")
    print(f"  - セル寸法        : Lx = {cell[0,0]:.4f} Å, Ly = {cell[1,1]:.4f} Å, Lz = {cell[2,2]:.4f} Å")
    print(f"  - スラブ実厚さ    : {thickness:.4f} Å")
    print(f"  - 各原子層のz座標 : {z_unique} Å")
    print(f"  - 層間距離 dz     : {diffs} Å (両端密結合 0.8881 Å, 中央粗結合 1.7758 Å)")
    print(f"  - 下部真空層厚さ  : {np.min(pos[:, 2]):.4f} Å")
    print(f"  - 上部真空層厚さ  : {cell[2,2] - np.max(pos[:, 2]):.4f} Å")
    print("============================================================")

    # 4. 初期構造ファイル (.cif, .xyz, .data) の出力
    slab_prefix = os.path.join(out_dir, "2H-SiC_10-10_slab_3x3x2_vac0.5A")
    ase.io.write(f"{slab_prefix}.cif", slab_3x3)
    ase.io.write(f"{slab_prefix}.xyz", slab_3x3)
    write_lammps_data(f"{slab_prefix}.data", slab_3x3, atom_style="atomic", masses=True)


if __name__ == "__main__":
    build_2periods_vac0_5a_slab()

