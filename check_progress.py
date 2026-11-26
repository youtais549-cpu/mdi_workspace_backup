#!/usr/bin/env python3
"""
第一原理MD / 構造緩和 計算進捗リアルタイム監視ツール
【実行方法】
python3 check_progress.py
または
./check_progress.py
"""
import os
import sys
import subprocess

SSH_CONFIG = "/home/yamazaki/mdi_workspace_backup/.ssh/config"
WORK_DIR = "/content/2H-SiC_10-10_slab_vac5A_relaxed_20261020"

def run_ssh(cmd):
    ssh_cmd = f'ssh -F {SSH_CONFIG} colab "{cmd}"'
    res = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def main():
    print("==================================================")
    print(" 🚀 2H-SiC スラブ計算 (Colab T4 GPU) 進捗モニター")
    print("==================================================")
    
    # 1. GPU 状態の確認
    cmd_gpu = "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits"
    out_gpu, _, code = run_ssh(cmd_gpu)
    
    if code != 0 or not out_gpu:
        print("❌ Colab への SSH 接続に失敗しました。トンネルが稼働しているか確認してください。")
        sys.exit(1)
        
    parts = [p.strip() for p in out_gpu.split(",")]
    if len(parts) >= 5:
        util, mem_used, mem_total, temp, power = parts
        print(f"【GPU 稼働状況】 Tesla T4")
        print(f"  ・GPU 使用率 : {util}%")
        print(f"  ・VRAM 使用量: {mem_used} / {mem_total} MiB")
        print(f"  ・GPU 温度   : {temp} ℃")
        print(f"  ・消費電力   : {power} W")
    print("--------------------------------------------------")

    # 2. プロセス稼働確認
    cmd_ps = "ps aux | grep -E '(lmp|pw.x.real|qe_mdi)' | grep -v grep"
    out_ps, _, _ = run_ssh(cmd_ps)
    if not out_ps:
        print("⚠️ 現在、計算プロセス (lmp / pw.x) は動いていません（完了または停止）。")
    else:
        print("【稼働中プロセス】")
        for line in out_ps.splitlines():
            cols = line.split()
            if len(cols) >= 11:
                pid, cpu, mem, cmd = cols[1], cols[2], cols[3], " ".join(cols[10:])
                print(f"  ・PID {pid:5s} | CPU: {cpu:>4s}% | MEM: {mem:>4s}% | {cmd[:50]}")
    print("--------------------------------------------------")

    # 3. LAMMPS 構造緩和ステップの確認
    cmd_lmp = f"grep -E '^[ ]+[0-9]+[ ]+' {WORK_DIR}/log.lammps | tail -n 5"
    out_lmp, _, _ = run_ssh(cmd_lmp)
    print("【LAMMPS 構造緩和ステップ (直近のエネルギー推移)】")
    if out_lmp:
        print("   Step   Temp     E_pair     E_mol      TotEng [eV]     Press")
        for line in out_lmp.splitlines():
            print(f"  {line}")
    else:
        print("  （現在、第 0 ステップの DFT 計算を実行中です...）")
    print("--------------------------------------------------")

    # 4. Quantum ESPRESSO 最新イテレーション
    cmd_qe = f"grep -E '(iteration #|total energy              =|convergence has been achieved)' {WORK_DIR}/espresso.pwo | tail -n 6"
    out_qe, _, _ = run_ssh(cmd_qe)
    print("【Quantum ESPRESSO 最新 SCF 収束状況】")
    if out_qe:
        for line in out_qe.splitlines():
            print(f"  {line.strip()}")
    else:
        print("  （電子密度収束計算を開始しています...）")
    print("==================================================")
    print("💡 リアルタイム連続監視したい場合は以下を実行してください:")
    print("   watch -n 10 python3 check_progress.py")
    print("==================================================")

if __name__ == "__main__":
    main()
