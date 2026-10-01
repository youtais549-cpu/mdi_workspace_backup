#!/bin/bash

# 1. 以前の古いログや一時ファイルをクリーンアップ
rm -rf tmp qe.out qe_mdi.pwo qe_mdi.pwi dump.lammpstrj qe_engine.log

echo "=== LAMMPS (ドライバー/MDIサーバー) を起動中... ==="
# LAMMPSをバックグラウンド（&）で起動し、ポート 8021 を開いてサーバー待機させます
lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021" -in in.lammps &
LMP_PID=$!

# LAMMPSがポートを確実に開くまで1秒待機
sleep 1

echo "=== Python/ASE MDI エンジン (中継スクリプト) を起動して結合計算を開始します... ==="
# Python+ASE MDI エンジンをフォアグラウンドで起動し、LAMMPSの8021ポートへクライアント接続します
python3 qe_mdi_engine.py -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" | tee qe_engine.log

# LAMMPSのMD計算が完全に終わるのを待機
wait $LMP_PID

echo "=== すべての計算が正常に完了しました！ ==="