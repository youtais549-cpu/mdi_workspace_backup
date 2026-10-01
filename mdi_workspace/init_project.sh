#!/bin/bash
# LAMMPS + Quantum ESPRESSO (MDI) 専用の新規計算フォルダ高速作成スクリプト

if [ -z "$1" ]; then
    echo "エラー: 新しく作成するフォルダ名を指定してください！"
    echo "使用例: ./init_project.sh new_simulation_01"
    exit 1
fi

NEW_DIR="$1"
TEMPLATE_DIR="$HOME/mdi_workspace/test_run"

echo "=== 新規 MDI シミュレーション環境を構築中: $NEW_DIR ==="
mkdir -p "$NEW_DIR"

# コアとなるスクリプト・設定ファイル・擬似ポテンシャル(.upf)をコピー
cp "$TEMPLATE_DIR/run.sh" "$NEW_DIR/"
cp "$TEMPLATE_DIR/qe_mdi_engine.py" "$NEW_DIR/"
cp "$TEMPLATE_DIR/make_xyz.py" "$NEW_DIR/"
cp "$TEMPLATE_DIR/in.lammps" "$NEW_DIR/"
cp "$TEMPLATE_DIR/"*.upf "$NEW_DIR/"

# スクリプトに実行権限の付与
chmod +x "$NEW_DIR/run.sh" "$NEW_DIR/make_xyz.py"

echo "✔ すべての環境が新フォルダ [$NEW_DIR] へ複製されました！"
echo ""
echo "🚀 実行手順:"
echo "   cd $NEW_DIR"
echo "   ./run.sh              # 結合分子動力学のスタート"
echo "   python3 make_xyz.py     # Winmostar 用トラジェクトリ変換"
echo "   wm md_animation.xyz   # Winmostar で即座に可視化！"
