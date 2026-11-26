#!/bin/bash
pwo="/mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo"
dump="/mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj"

last_dump_count=$(grep -c "ITEM: TIMESTEP" "$dump")
last_pwo_mod=$(stat -c %Y "$pwo")
no_update_counter=0

echo "Monitoring started. Initial dump blocks: $last_dump_count"

while true; do
  sleep 300 # 5分ごとにチェック
  
  # ダンプファイルの更新チェック
  current_dump_count=$(grep -c "ITEM: TIMESTEP" "$dump")
  if [ "$current_dump_count" -gt "$last_dump_count" ]; then
    echo "PROGRESS: Dump file updated! New block count: $current_dump_count"
    exit 0
  fi
  
  # pwoファイルの更新（計算の進行）チェック
  current_pwo_mod=$(stat -c %Y "$pwo")
  if [ "$last_pwo_mod" -eq "$current_pwo_mod" ]; then
    no_update_counter=$((no_update_counter + 1))
  else
    no_update_counter=0
    last_pwo_mod=$current_pwo_mod
  fi
  
  # 30分間（5分×6回）更新がなければ停止とみなす
  if [ "$no_update_counter" -ge 6 ]; then
    echo "ERROR: espresso.pwo has not been updated for 30 minutes! Calculation stopped."
    exit 1
  fi
done
