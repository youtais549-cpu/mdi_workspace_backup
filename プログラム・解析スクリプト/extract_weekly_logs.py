import os
import json
import sys
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    print("Usage: python3 extract_weekly_logs.py <output_file>")
    sys.exit(1)

output_file = sys.argv[1]
brain_dir = "/home/yamazaki/.gemini/antigravity-ide/brain/"
one_week_ago = datetime.now() - timedelta(days=7)

with open(output_file, 'w', encoding='utf-8') as out_f:
    out_f.write("=== 直近1週間の会話ログ ===\n\n")
    
    # List all directories in brain_dir
    for conv_id in os.listdir(brain_dir):
        conv_dir = os.path.join(brain_dir, conv_id)
        if not os.path.isdir(conv_dir):
            continue
            
        transcript_path = os.path.join(conv_dir, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            continue
            
        mtime = datetime.fromtimestamp(os.path.getmtime(transcript_path))
        if mtime < one_week_ago:
            continue
            
        out_f.write(f"--- 会話ID: {conv_id} ({mtime.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
        
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'USER_INPUT':
                            out_f.write(f"\n[USER]\n{data.get('content', '')}\n")
                        elif data.get('type') == 'PLANNER_RESPONSE':
                            out_f.write(f"\n[AI]\n{data.get('content', '')}\n")
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            out_f.write(f"エラー: {e}\n")
            
        out_f.write("\n" + "="*40 + "\n\n")

print(f"Log extracted to {output_file}")
