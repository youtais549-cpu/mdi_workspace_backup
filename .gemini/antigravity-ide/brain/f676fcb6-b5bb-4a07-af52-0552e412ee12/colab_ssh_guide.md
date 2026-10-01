# Google ColabをSSHサーバー化して直接接続する方法 (Cloudflared経由)

Google Colaboratoryのランタイムを擬似的なリモートサーバー（SSHサーバー）として扱い、このアプリのターミナルから直接コマンドを実行したり、ファイルを転送したりする手順を解説します。

今回は、無料でポート開放設定が不要な **Cloudflared（colab_sshライブラリ）** を使用した最も簡単な方法をご紹介します。

---

## Step 1: Google Colab側での準備

まずはColabのランタイムを起動し、SSH接続の待ち受け状態にします。

1. **Google Colabで新しいノートブックを作成** します（または既存のセットアップ用ノートブックを開きます）。
2. GPUを使用する場合は、メニューの「ランタイム」>「ランタイムのタイプを変更」から **GPU** を選択しておきます。
3. 以下のコードをセルに貼り付けて実行します。

```python
# colab-ssh パッケージをインストール
!pip install colab_ssh --upgrade

from colab_ssh import launch_ssh_cloudflared

# パスワードを自由に設定してください（例: "mypassword"）
# ※ このパスワードはSSH接続時に使用します
launch_ssh_cloudflared(password="mypassword")
```

4. セルの実行が完了すると、出力結果に以下のような **SSH接続用のコマンド** が表示されます。これをメモ（コピー）してください。
   *例:*
   `ssh -o UserKnownHostsFile=/dev/null -o VisualHostKey=yes -p 22 root@xxxxx.trycloudflare.com`

---

## Step 2: このアプリ（ローカル環境）側の準備

このアプリの環境からCloudflared経由でColabに接続するためには、ローカル側にも `cloudflared` コマンドがインストールされている必要があります。

1. **このアプリのターミナルを開きます**。
2. 以下のコマンドを実行して `cloudflared` をインストールします（Linuxの場合）。

```bash
# cloudflaredのダウンロードとインストール
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```
*(※もしsudoが使えない環境であれば、バイナリを直接ダウンロードしてパスを通す方法で実行可能です。)*

3. SSHのコンフィグファイル（`~/.ssh/config`）に、Cloudflare経由で接続するための設定を追記します。ターミナルで以下を実行します。

```bash
mkdir -p ~/.ssh
cat << 'EOF' >> ~/.ssh/config

Host *.trycloudflare.com
    HostName %h
    User root
    Port 22
    ProxyCommand cloudflared access ssh --hostname %h
EOF
```

---

## Step 3: ColabへSSH接続する

設定が完了したら、実際にColabへ接続します。

1. このアプリのターミナルで、**Step 1** で表示された `root@xxxxx.trycloudflare.com` の部分を使ってSSH接続を行います。

```bash
ssh root@xxxxx.trycloudflare.com
```

2. 接続時に `Are you sure you want to continue connecting (yes/no/[fingerprint])?` と聞かれたら `yes` と入力します。
3. パスワードを求められるので、Step 1で設定したパスワード（例: `mypassword`）を入力します。

成功すると、ターミナルのプロンプトが `root@xxxxxx:/content#` のようになり、Colabの環境内部に入ることができます。

---

## Step 4: ファイルを転送して実行する

SSH接続ができるようになると、`scp`（または `rsync`）を使って、ローカルの `mdi_workspace` をColabに直接送ることができます。

**別のターミナルタブを開き**（またはSSH接続を切断して）、以下のコマンドでファイルをColabに送ります。

```bash
# 例: SiC_3x3x10_MD フォルダごとColabの /content/ に送る
scp -r /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD root@xxxxx.trycloudflare.com:/content/
```

転送が終わったら、再度SSHでColabに入り、計算を実行します。

```bash
ssh root@xxxxx.trycloudflare.com

cd /content/SiC_3x3x10_MD
# バックグラウンドで実行
nohup bash run_colab.sh > nohup.out 2>&1 &

# ログを確認
tail -f nohup.out
```

計算が完了したら、結果をローカルに取り寄せます。

```bash
# ローカル側のターミナルで実行（Colabからファイルをダウンロード）
scp -r root@xxxxx.trycloudflare.com:/content/SiC_3x3x10_MD/dump.lammpstrj /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/
```

---

## ⚠️ 注意点
- **ランタイムの制限**: Google Colabのランタイムは、アイドル状態が長く続いたり、最長12時間（プロ版は24時間）経過したりすると強制終了し、データがすべて消えます。重要な出力データは計算完了後すぐにローカルに `scp` で取得するか、Google DriveをColab上でマウントしてそちらに保存するよう設定してください。
- **インスタンスが変わる**: Colabのランタイムを再起動するたびに、`trycloudflare.com` のURLは毎回変わります。接続のたびにStep 1のセルを実行してURLを確認してください。
