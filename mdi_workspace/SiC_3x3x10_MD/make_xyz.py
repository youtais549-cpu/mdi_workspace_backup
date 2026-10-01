#!/usr/bin/env python3
import sys
from ase.io import read, write

def convert_lammps_to_xyz(dump_file="dump_min.lammpstrj", output_file="md_animation.xyz"):
    print(f"[Convert] 読み込み中: {dump_file} ...")
    try:
        # LAMMPS のトラジェクトリをすべてのフレーム（index=":"）でロード
        trajectory = read(dump_file, index=":", format="lammps-dump-text")
        
        # LAMMPSの整数タイプ (1, 2) を 正しい元素記号 (Si, C) に再マッピング
        for atoms in trajectory:
            symbols = []
            for num in atoms.get_atomic_numbers():
                # タイプ 1 (あるいは誤認識番号) を Si に、タイプ 2 を C に割り当てる
                if num == 1 or num == 14:
                    symbols.append("Si")
                elif num == 2 or num == 6:
                    symbols.append("C")
                else:
                    symbols.append("Si")
            atoms.set_chemical_symbols(symbols)
            
        write(output_file, trajectory)
        print(f"[Convert] 全 {len(trajectory)} 完了！出力ファイル: {output_file}")
        print("💡 次のコマンドで可視化できます: wm md_animation.xyz")
    except Exception as e:
        print(f"変換中にエラーが発生しました: {e}", file=sys.stderr)

if __name__ == "__main__":
    dump_path = sys.argv[1] if len(sys.argv) > 1 else "dump_min.lammpstrj"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "md_animation.xyz"
    convert_lammps_to_xyz(dump_path, out_path)
