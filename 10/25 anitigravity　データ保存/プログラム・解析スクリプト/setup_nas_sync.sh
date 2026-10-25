#!/bin/bash
# NAS同期セットアップ＆実行スクリプト（Backup と Results 両方対応版）

echo "=== NAS への自動同期システム (2箇所同時バックアップ) ==="
echo "※実行にはWSL(Linux)の管理者権限(sudo)が必要なため、パスワードを求められる場合があります。"

if ! dpkg -l | grep -q cifs-utils; then
    echo "cifs-utilsをインストールしています..."
    sudo apt-get update && sudo apt-get install -y cifs-utils
fi

echo ""
echo "NAS (192.168.12.69) に接続するための情報を入力してください。"
read -p "NASのユーザー名: " NAS_USER
read -s -p "NASのパスワード: " NAS_PASS
echo ""

# マウントポイントの作成
sudo mkdir -p /mnt/nas_backup
sudo mkdir -p /mnt/nas_results
sudo mkdir -p /mnt/g

# Gドライブ（Google Drive）のマウント確認と実行
if ! mountpoint -q /mnt/g; then
    echo "GドライブをWSLにマウントしています..."
    sudo mount -t drvfs G: /mnt/g
fi

# NASのマウント (Backup 共有フォルダ)
if ! mountpoint -q /mnt/nas_backup; then
    echo "NAS (Backup) をWSLにマウントしています..."
    sudo mount -t cifs //192.168.12.69/Backup /mnt/nas_backup -o username="${NAS_USER}",password="${NAS_PASS}",vers=3.0,uid=$(id -u),gid=$(id -g)
fi

# NASのマウント (Results 共有フォルダ)
if ! mountpoint -q /mnt/nas_results; then
    echo "NAS (Results) をWSLにマウントしています..."
    sudo mount -t cifs //192.168.12.69/Results /mnt/nas_results -o username="${NAS_USER}",password="${NAS_PASS}",vers=3.0,uid=$(id -u),gid=$(id -g)
    if [ $? -ne 0 ]; then
        echo "❌ Results フォルダのマウントに失敗しました。アクセス権限等を確認してください。"
        exit 1
    fi
fi

# NAS側のバックアップ先フォルダ作成
NAS_TARGET_BACKUP="/mnt/nas_backup/Yamazaki-tj/SiC_MD_backup"
NAS_TARGET_RESULTS="/mnt/nas_results/yamazaki/research/SiC_MD_backup"

mkdir -p "$NAS_TARGET_BACKUP"
mkdir -p "$NAS_TARGET_RESULTS"

echo "✅ すべてのマウント成功！"

# 定期同期用スクリプト（バックグラウンド動作）を作成
cat << 'EOF' > ~/nas_sync_loop.sh
#!/bin/bash
NAS_TARGET_BACKUP="/mnt/nas_backup/Yamazaki-tj/SiC_MD_backup"
NAS_TARGET_RESULTS="/mnt/nas_results/yamazaki/research/SiC_MD_backup"

# Google Driveのフォルダ名判定
if [ -d "/mnt/g/マイドライブ/SiC_MD_backup" ]; then
    GDRIVE_DIR="/mnt/g/マイドライブ/SiC_MD_backup"
elif [ -d "/mnt/g/MyDrive/SiC_MD_backup" ]; then
    GDRIVE_DIR="/mnt/g/MyDrive/SiC_MD_backup"
elif [ -d "/mnt/g/My Drive/SiC_MD_backup" ]; then
    GDRIVE_DIR="/mnt/g/My Drive/SiC_MD_backup"
else
    GDRIVE_DIR="/mnt/g/SiC_MD_backup" 
fi

while true; do
    if [ -d "$GDRIVE_DIR" ]; then
        # rsyncで差分だけを2箇所のNASにコピー
        rsync -av --update "$GDRIVE_DIR/" "$NAS_TARGET_BACKUP/" > /dev/null 2>&1
        rsync -av --update "$GDRIVE_DIR/" "$NAS_TARGET_RESULTS/" > /dev/null 2>&1
    fi
    sleep 600
done
EOF

chmod +x ~/nas_sync_loop.sh

# 古いバックグラウンドプロセスがあればキルする
pkill -f nas_sync_loop.sh 2>/dev/null

# バックグラウンドで実行開始
nohup ~/nas_sync_loop.sh > ~/nas_sync.log 2>&1 &

echo "✅ 裏側での同期が開始されました！（10分おきにGoogle Driveのデータを Backup と Results の2箇所に同時コピーします）"
