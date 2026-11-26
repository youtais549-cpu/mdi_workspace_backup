#!/usr/bin/env python3
"""
Google Colab (T4 GPU) 遠隔連携ワークフロースクリプト
ローカルから Colab への SSH 接続、GPU 状態確認、ファイル転送、実行、ログ監視を統括します。
"""
import sys
import os
import subprocess

LOCAL_DIR = "/home/yamazaki/mdi_workspace_backup/mdi_workspace/SiC_3x3x2_10-10_MD"
REMOTE_DIR = "/content/SiC_3x3x2_10-10_MD"
SSH_CONFIG = "/home/yamazaki/mdi_workspace_backup/.ssh/config"

def run_ssh(cmd, capture=False):
    ssh_cmd = f'ssh -F {SSH_CONFIG} colab "{cmd}"'
    if capture:
        res = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        return res.stdout, res.stderr, res.returncode
    else:
        return subprocess.run(ssh_cmd, shell=True).returncode

def check_connection():
    print("==========================================")
    print(" 1. Colab への SSH 接続および GPU 状態確認")
    print("==========================================")
    print("Colab への疎通を確認中...")
    out, err, code = run_ssh("nvidia-smi", capture=True)
    if code != 0:
        print(f"❌ SSH接続またはGPU認識に失敗しました:\n{err}")
        print("\n💡 ヒント: Colab 上で ngrok や cloudflared トンネルが起動しているか確認してください。")
        print(f"   現在の SSH 設定: {SSH_CONFIG}")
        return False
    print("✅ SSH 接続成功！ T4 GPU の稼働を確認しました:")
    print(out)
    return True

def upload_files():
    print("==========================================")
    print(" 2. ローカルから Colab へファイルを転送 (SCP)")
    print("==========================================")
    run_ssh(f"mkdir -p {REMOTE_DIR}")
    scp_cmd = f'scp -F {SSH_CONFIG} -r {LOCAL_DIR}/* colab:{REMOTE_DIR}/'
    print(f"転送中: {LOCAL_DIR} -> colab:{REMOTE_DIR}/")
    code = subprocess.run(scp_cmd, shell=True).returncode
    if code == 0:
        print("✅ ファイルの転送が完了しました！")
        return True
    else:
        print("❌ 転送に失敗しました。")
        return False

def start_calculation():
    print("==========================================")
    print(" 3. Colab 上で T4 GPU 計算を開始 (master_run_gpu.sh)")
    print("==========================================")
    # 古いプロセスの停止
    run_ssh("killall -9 pw.x lmp 2>/dev/null || true")
    # マスタースクリプトの実行
    cmd = f"cd {REMOTE_DIR} && (nohup bash master_run_gpu.sh </dev/null >master.log 2>&1 &) && sleep 1"
    code = run_ssh(cmd)
    if code == 0:
        print("🚀 Colab 上で計算がバックグラウンド開始されました！")
        print("進行状況の確認: python3 run_colab_gpu_workflow.py log")
        return True
    return False

def show_status():
    print("==========================================")
    print(" 実行中プロセスの確認 (Colab)")
    print("==========================================")
    run_ssh("ps aux | grep -E 'pw.x|lmp|python3 qe_mdi' | grep -v grep || echo '実行中の計算プロセスはありません。'")

def tail_log():
    print("==========================================")
    print(" 進行状況ログのリアルタイム表示 (Ctrl+C で終了)")
    print("==========================================")
    try:
        run_ssh(f"tail -f {REMOTE_DIR}/nohup.out 2>/dev/null || tail -f {REMOTE_DIR}/qe_engine.log")
    except KeyboardInterrupt:
        print("\nログ監視を終了しました（計算はバックグラウンドで継続中）。")

def configure_ssh(args):
    """SSH接続先 (ngrokホスト・ポート) の更新"""
    if len(args) == 1:
        raw = args[0].replace("tcp://", "")
        if ":" in raw:
            host, port = raw.split(":")
        else:
            print("❌ 書式エラー: 'host:port' または 'host port' で指定してください。")
            return False
    elif len(args) >= 2:
        host, port = args[0], args[1]
    else:
        print("❌ 引数が不足しています。例: python3 run_colab_gpu_workflow.py config 8.tcp.ngrok.io 17016")
        return False

    content = f"""Host colab
    HostName {host}
    User root
    Port {port}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    IdentityFile /home/yamazaki/mdi_workspace_backup/.ssh/id_ed25519
    LogLevel ERROR
"""
    os.makedirs(os.path.dirname(SSH_CONFIG), exist_ok=True)
    with open(SSH_CONFIG, "w") as f:
        f.write(content)
    print(f"✅ SSH設定を更新しました:\n  HostName: {host}\n  Port: {port}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "check":
            check_connection()
        elif mode == "upload":
            upload_files()
        elif mode == "start":
            start_calculation()
        elif mode == "status":
            show_status()
        elif mode == "log":
            tail_log()
        elif mode == "config":
            configure_ssh(sys.argv[2:])
        elif mode == "all":
            if check_connection() and upload_files():
                start_calculation()
                tail_log()
        else:
            print(f"未定義のコマンド: {mode}")
    else:
        print("=== Google Colab (T4 GPU) 連携ツール ===")
        print("使い方:")
        print("  python3 run_colab_gpu_workflow.py config <host> <port> : SSH接続情報(ngrok)を更新")
        print("  python3 run_colab_gpu_workflow.py check                : Colab SSH接続とGPU(nvidia-smi)確認")
        print("  python3 run_colab_gpu_workflow.py upload               : 72原子モデル一式を Colab へアップロード")
        print("  python3 run_colab_gpu_workflow.py start                : Colab 上で T4 GPU 計算を開始")
        print("  python3 run_colab_gpu_workflow.py status               : 実行中プロセスの確認")
        print("  python3 run_colab_gpu_workflow.py log                  : リアルタイムログ監視")
        print("  python3 run_colab_gpu_workflow.py all                  : 確認 -> 転送 -> 開始 -> ログ監視を一括実行")
