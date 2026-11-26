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
