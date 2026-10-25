#!/usr/bin/env python3
"""
stream_iteration.py (バッファリングフリー & ライブハートビート搭載版)
Colab T4 GPU 上で実行中の Quantum ESPRESSO (pw.x) の SCF iteration を
リアルタイムで完全遅延ゼロでストリーミング表示するスクリプト。

【特徴】
1. SSH疑似端末 (-tt) と stdbuf による完全バッファリング解除
2. イテレーション計算中（1分間の沈黙時）も「⏳ 計算中 (〇秒経過...)」をライブ表示
3. 自動ファイル検出（6周期リスタート最優先）
"""

import sys
import os
import subprocess
import re
import time
import datetime
import threading

# ANSIカラーコード
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"
CLEAR_LINE = "\033[2K\r"

REMOTE_FILE = "/content/calc_2H-SiC_10-10_2periods_vac2.5A_2nd/espresso.pwo"
if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
    REMOTE_FILE = sys.argv[1]

# SSH -tt で疑似端末を割り当て、リモートの stdbuf -oL で行バッファリングを強制
SSH_CMD = [
    "ssh", "-tt",
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=10",
    "-o", "LogLevel=ERROR",
    "colab",
    f"stdbuf -oL tail -f -n 40 {REMOTE_FILE}"
]

# ライブステータス共有変数
running = True
current_iter = "準備中"
last_update_time = time.time()
spin_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
spin_idx = 0

def heartbeat_thread():
    """計算中の沈黙時間でもターミナルが生きていることを示すスピナー表示スレッド"""
    global spin_idx
    while running:
        elapsed = int(time.time() - last_update_time)
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        spinner = spin_chars[spin_idx % len(spin_chars)]
        spin_idx += 1
        
        # 画面最下行に動的ステータスを表示
        sys.stdout.write(f"{CLEAR_LINE}{DIM}[{now_str}]{RESET} {CYAN}{spinner} Iteration #{current_iter} 計算中... ({elapsed}s 経過){RESET} ")
        sys.stdout.flush()
        time.sleep(0.5)

def main():
    global running, current_iter, last_update_time
    raw_mode = "--raw" in sys.argv

    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}  Quantum ESPRESSO リアルタイム Iteration モニター (Colab T4 GPU)  {RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{DIM}監視対象: {REMOTE_FILE}{RESET}")
    print(f"{DIM}中断するには [Ctrl + C] を押してください。{RESET}\n")

    proc = subprocess.Popen(
        SSH_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # ハートビートスレッド開始
    hb = threading.Thread(target=heartbeat_thread, daemon=True)
    hb.start()

    current_time_spent = None

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
                continue

            line = line.replace("\r", "").rstrip("\n")
            if not line.strip():
                continue

            last_update_time = time.time()

            if raw_mode:
                sys.stdout.write(f"{CLEAR_LINE}{line}\n")
                sys.stdout.flush()
                continue

            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            # 1. iteration 開始の検知
            iter_match = re.search(r"iteration #\s*(\d+)", line)
            if iter_match:
                current_iter = iter_match.group(1)
                sys.stdout.write(f"{CLEAR_LINE}[{now_str}] {BOLD}{CYAN}▶ Iteration #{current_iter:>2}{RESET} 開始...\n")
                sys.stdout.flush()
                continue

            # 2. CPU time
            time_match = re.search(r"total cpu time spent up to now is\s+([\d\.]+)\s+secs", line)
            if time_match:
                current_time_spent = time_match.group(1)
                continue

            # 3. total energy の検知
            energy_match = re.search(r"total energy\s+=\s+([-\d\.]+)\s+Ry", line)
            if energy_match:
                e_ry = float(energy_match.group(1))
                e_ev = e_ry * 13.6056980659
                sys.stdout.write(f"{CLEAR_LINE}         {GREEN}⚡ Total Energy : {e_ry:16.8f} Ry  ({e_ev:12.4f} eV){RESET}\n")
                sys.stdout.flush()
                continue

            # 4. estimated scf accuracy の検知
            acc_match = re.search(r"estimated scf accuracy\s+<\s+([\d\.E\+\-]+)\s+Ry", line)
            if acc_match:
                acc = acc_match.group(1)
                time_info = f" (累計時間: {current_time_spent}s)" if current_time_spent else ""
                sys.stdout.write(f"{CLEAR_LINE}         {YELLOW}🎯 SCF Accuracy : < {acc:>14} Ry{RESET}{DIM}{time_info}{RESET}\n")
                sys.stdout.flush()
                continue

            # 5. 収束達成
            if "convergence has been achieved" in line:
                sys.stdout.write(f"{CLEAR_LINE}\n[{now_str}] {BOLD}{GREEN}🎉 [SCF 収束達成] convergence has been achieved in {current_iter} iterations!{RESET}\n\n")
                sys.stdout.flush()
                continue

            # 6. 力の計算
            if "Forces acting on atoms" in line:
                sys.stdout.write(f"{CLEAR_LINE}[{now_str}] {MAGENTA}💪 各原子への作用力を計算中...{RESET}\n")
                sys.stdout.flush()
                continue

            # 7. CGステップ進行
            if "Total force =" in line:
                sys.stdout.write(f"{CLEAR_LINE}         {MAGENTA}{line.strip()}{RESET}\n")
                sys.stdout.flush()
                continue

    except KeyboardInterrupt:
        pass
    finally:
        running = False
        sys.stdout.write(f"{CLEAR_LINE}\n{YELLOW}モニターを終了しました。{RESET}\n")
        sys.stdout.flush()
        if proc.poll() is None:
            proc.terminate()

if __name__ == "__main__":
    main()
