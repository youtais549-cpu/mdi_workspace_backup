---
description: Google Driveのマウント認証（rclone）を行う際の必須手順
---

# Google Drive Headless Authentication

この環境（画面なしのLinuxサーバー）で `rclone` 等を用いてGoogle Driveをマウントする際は、Googleのセキュリティ制限により「ヘッドレス環境でのURL発行による認証（Out-of-band認証）」がブロックされて失敗します。

そのため、エージェントはマウント処理を行う際、以下の手順を必ずユーザーに案内してください。

1. ユーザー自身のローカルPC（Windowsなど）に `rclone` をインストールしてもらう。
2. ローカルPCのコマンドラインで `rclone authorize "drive"` を実行してもらう。
3. ブラウザで認証後、ターミナルに出力されるトークン（`{"access_token":...}` を含む文字列）をチャットに貼り付けてもらう。
4. エージェントはそのトークンを使用して `~/.config/rclone/rclone.conf` を作成し、マウントを行う。

**禁止事項:**
- エージェント自身が `rclone config` のインタラクティブフローを進めたり、`google-drive-ocamlfuse -headless` でURLを発行してユーザーにアクセスさせようと試みること（必ず失敗するため）。
