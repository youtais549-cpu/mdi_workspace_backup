#!/usr/bin/env python3
"""
==============================================================================
Google Colab (T4 GPU) 遠隔連携 CLI ツール
【固定コアコード: ユーザー編集不要】
==============================================================================
ローカルから Colab への SSH 接続設定、GPU 状態確認、
任意の計算ディレクトリのアップロード、バックグラウンド起動、ログ監視を統括します。
"""
import sys
import os
import subprocess

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
        print("❌ 引数が不足しています。例: python3 workflow_cli.py config 8.tcp.us-cal-1.ngrok.io 19545")
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

def upload_calculation_dir(local_dir, remote_name=None):
    if not os.path.exists(local_dir):
        print(f"❌ ディレクトリが見つかりません: {local_dir}")
        return False
    
    dir_name = remote_name if remote_name else os.path.basename(os.path.abspath(local_dir))
    remote_path = f"/content/{dir_name}"
    
    print("==========================================")
    print(f" 2. 計算ディレクトリを Colab へアップロード")
    print(f"    ローカル: {local_dir}")
    print(f"    Colab   : {remote_path}")
    print("==========================================")
    run_ssh(f"mkdir -p {remote_path}")
    
    # コア実行ファイル(run_colab_gpu.sh, master_run_gpu.sh, make_xyz.py, qe_mdi_engine_core.py)も含めて転送
    core_dir = os.path.dirname(os.path.abspath(__file__))
    cmd_core = f"scp -F {SSH_CONFIG} {core_dir}/* colab:{remote_path}/ 2>/dev/null || true"
    subprocess.run(cmd_core, shell=True)
    
    # ユーザーの計算ファイル(構造データ, in.lammps, dft_settings.py, 擬ポテンシャル等)を転送
    cmd_user = f"scp -F {SSH_CONFIG} -r {local_dir}/* colab:{remote_path}/"
    code = subprocess.run(cmd_user, shell=True).returncode
    if code == 0:
        print("✅ ファイルの転送が完了しました！")
        return True
    else:
        print("❌ 転送に失敗しました。")
        return False

def start_calculation(remote_dir_name):
    remote_path = f"/content/{remote_dir_name}"
    print("==========================================")
    print(f" 3. Colab 上で計算を開始 ({remote_path})")
    print("==========================================")
    run_ssh("killall -9 pw.x lmp 2>/dev/null || true")
    cmd = f"cd {remote_path} && nohup bash master_run_gpu.sh > master.log 2>&1 &"
    code = run_ssh(cmd)
    if code == 0:
        print("🚀 Colab 上で計算がバックグラウンド開始されました！")
        print(f"進行状況ログの確認: python3 workflow_cli.py log {remote_dir_name}")
        return True
    return False

def show_status():
    print("==========================================")
    print(" 実行中プロセスの確認 (Colab)")
    print("==========================================")
    run_ssh("ps aux | grep -E 'pw.x|lmp|python3 qe_mdi' | grep -v grep || echo '実行中の計算プロセスはありません。'")

def tail_log(remote_dir_name="SiC_3x3x2_10-10_MD"):
    remote_path = f"/content/{remote_dir_name}"
    print("==========================================")
    print(f" 進行状況ログのリアルタイム表示 ({remote_path})")
    print(" (Ctrl+C で離脱しても計算は継続します)")
    print("==========================================")
    try:
        run_ssh(f"tail -f {remote_path}/nohup.out 2>/dev/null || tail -f {remote_path}/qe_engine.log")
    except KeyboardInterrupt:
        print("\nログ監視を終了しました。")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "config":
            configure_ssh(sys.argv[2:])
        elif cmd == "check":
            check_connection()
        elif cmd == "upload":
            target = sys.argv[2] if len(sys.argv) > 2 else "."
            upload_calculation_dir(target)
        elif cmd == "start":
            target = sys.argv[2] if len(sys.argv) > 2 else "calc_run"
            start_calculation(target)
        elif cmd == "status":
            show_status()
        elif cmd == "log":
            target = sys.argv[2] if len(sys.argv) > 2 else "calc_run"
            tail_log(target)
        else:
            print(f"未定義のコマンド: {cmd}")
    else:
        print("=== Google Colab (T4 GPU) ワークフロー CLI ===")
        print("使い方:")
        print("  python3 workflow_cli.py config <host> <port>   : SSH接続情報(ngrok)を更新")
        print("  python3 workflow_cli.py check                  : Colab SSH接続とGPU(nvidia-smi)確認")
        print("  python3 workflow_cli.py upload <計算フォルダ>  : 計算一式を Colab へアップロード")
        print("  python3 workflow_cli.py start <リモート名>     : Colab 上で T4 GPU 計算を開始")
        print("  python3 workflow_cli.py status                 : 実行中プロセスの確認")
        print("  python3 workflow_cli.py log <リモート名>       : 進行状況ログのリアルタイム監視")
