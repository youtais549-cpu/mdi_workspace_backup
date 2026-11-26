from ase.io import read, write
from ase.build import make_supercell
import os

def create_supercell():
    # 1. CIFファイルの読み込み
    input_file = '2H-SiC.cif'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} が見つかりません。")
        return

    atoms = read(input_file)

    # 2. 3x3x2 の変換行列を定義
    # a軸方向に3倍, b軸方向に3倍, c軸方向に2倍
    transformation_matrix = [[3, 0, 0],
                             [0, 3, 0],
                             [0, 0, 2]]

    # スーパーセルの作成 (2層 x 2 = 4層になります)
    supercell = make_supercell(atoms, transformation_matrix)

    # 3. ファイルへの保存
    # 計算ソフトで扱いやすいCIF形式と、Winmostar等ですぐ見れるXYZ形式の両方を出力します
    write('2H-SiC_supercell_3x3x2.cif', supercell)
    write('2H-SiC_supercell_3x3x2.xyz', supercell)
    
    print("スーパーセルの作成が完了しました！")
    print(f"作成された原子数: {len(supercell)} 個")

if __name__ == '__main__':
    create_supercell()
