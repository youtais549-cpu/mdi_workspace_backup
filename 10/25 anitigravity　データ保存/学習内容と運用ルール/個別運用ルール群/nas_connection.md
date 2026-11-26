---
name: NAS Connection and Upload Rules
description: ネットワーク制限下でのNASへの安全なファイル転送方法
---

# NAS Connection Guidelines

この環境（仮想環境・コンテナ等）では、OS標準のカーネルマウント（`mount -t cifs`）がファイアウォールやセキュリティ制限によってフリーズする既知の問題があります。

今後、ファイルやバックアップをNAS（例: `//192.168.12.69/Backup`）へ送信するタスクを依頼された場合は、以下のルールに従ってください。

## ルール
1. **マウントコマンドの使用禁止**: `mount.cifs` は絶対に使用しないでください。
2. **smbclientの使用**: ファイルの転送には必ずユーザー空間で動作する `smbclient` コマンドを使用してください。
3. **認証情報の安全な取り扱い**: パスワードをコマンドラインに直接含めないでください。`~/.smbcredentials` などの認証ファイルを使用し、パーミッションは `600` に設定して `smbclient -A` で読み込ませてください。

## smbclientでのアップロード手順の例
```bash
smbclient "//192.168.12.69/Backup" -A "$HOME/.smbcredentials" -c 'cd "Yamazaki-tj\新しいフォルダー (2)"; put "local_file.txt" "remote_file.txt"'
```
