---
description: CIFファイルの閲覧とWinmostarの取り扱いに関するルール
---

# CIF File Viewing & Winmostar

この環境はLinuxベースで動作しているため、Windows専用のGUIアプリケーションである「Winmostar」をエディタ上で直接起動することはできません。

ユーザーが「CIFファイルをWinmostarで開きたい」「エディタ上で3D構造を見たい」と要望した場合は、以下の手順のいずれかを提案・実行してください。

1. **Winmostarで開きたい場合（ローカルでの実行）:**
   対象のCIFファイルをローカルのWindows PCへダウンロードし、手元のWinmostarで開くように案内する。

2. **エディタ上で3D構造を確認したい場合（推奨）:**
   - エディタの拡張機能（`3Dmol` など）のインストール方法を案内する。
   - または、`py3Dmol` を使用してCIFファイルをHTMLに変換するPythonスクリプト（`cif_viewer.py`など）を提供・実行し、生成されたHTMLファイルをエディタ上で開くように案内する。

**禁止事項:**
- Linux環境内で `winmostar` コマンドを探したり、インストールを試みること。
