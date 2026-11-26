# MD計算環境の構築完了レポート

3×3×10モデル（真空層付き）をLAMMPSとQuantum ESPRESSO（MDI連携）で実行するためのNVTアンサンブル環境の構築が完了しました。

## 構築された環境

シミュレーション環境はすべて新しいディレクトリ `~/mdi_workspace/SiC_3x3x10_MD` 内に構築されています。

### 1. LAMMPS用のデータ変換
追加の真空層（合計20 Å）を付与した `qe.in` の構造から、ASEスクリプトを利用して正確に LAMMPSデータファイル（[`2H-SiC_supercell_3x3x10_vacuum.data`](file:///home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/2H-SiC_supercell_3x3x10_vacuum.data)）への変換を行いました。これにより、Si原子とC原子の座標・セルサイズがLAMMPS側に正しく引き継がれます。

### 2. MD入力スクリプトの更新
[`in.lammps`](file:///home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/in.lammps) において以下の変更を適用しました。
- `read_data` で上記の作成したデータファイルを読み込むように設定しました。
- アンサンブルを `fix 2 all nvt temp 300.0 300.0 0.1` に変更し、設定通りの **NVTアンサンブル（300 K）** によるMDが実行されるようにしました。

## 今後の実行手順

> [!TIP]
> 第一原理MD計算は非常に時間がかかるため、バックグラウンドでの長期間実行に適したスラッシュコマンド `/goal` を使って私（Antigravity）に計算の実行とトラジェクトリ変換・可視化をすべて任せることも可能です。

以下のコマンドで計算をスタートできます：
```bash
cd ~/mdi_workspace/SiC_3x3x10_MD
./run.sh
```

計算終了後は `python3 make_xyz.py` でXYZ形式に変換し、 `wm md_animation.xyz` を実行すればすぐにWinmostarでの描画が可能です。
