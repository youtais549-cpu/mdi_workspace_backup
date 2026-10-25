# Learning Proposal v6 — Colab ランタイム再起動からの復旧・リスタート運用と監視スクリプト仕様

> [!IMPORTANT]
> 承認いただくまで **設定ファイルは一切変更していません**。下記の提案にご意見（採否・文言修正）をください。

## 1. 今回のセッションから抽出した学び

| # | 出来事 | 根本原因 | 再利用可能な教訓 |
|---|---|---|---|
| A | 14 時間稼働後に Colab が停止。新 ngrok URL を貼って再開 | Colab ランタイムの連続稼働制限。再起動で `/opt/nvidia/hpc_sdk` が消え、ngrok のホスト/ポートも変わる | 復旧手順が毎回必要（SSH config 更新 → NVHPC 再導入 → バイナリ再配置 → 最終フレームからリスタート） |
| B | ユーザーが Drive 上のフォルダ名を `[101_0]6周期５Å(境界条件変更)` に変更 | ユーザー側のリネーム | バックアップ先は固定文字列で決め打ちせず、実フォルダ名を `ls` で確認してから同期ループを張る |
| C | `sudo mount`（パスワード待ち）、`ssh ... cat`（無応答）、PowerShell 出力の文字化けでコマンドが固まった | WSL 環境の制約 | sudo/対話コマンド禁止、`ssh -o BatchMode=yes -o ConnectTimeout=10`、Drive へは PowerShell + `C:\temp_sic_sync` 経由 |
| D | `stream_iteration.py` が「止まって見える」 | 非 tty の SSH パイプが 4KB ブロックバッファ + 216 原子では 1 反復 ≈ 1 分で出力が疎 | `ssh -tt` + `stdbuf -oL` + ハートビート（スピナー/経過秒）が必須 |

## 2. 分類と方針

- **種別**: *Rule*（既存ルールの更新を優先）
- **更新対象**: [`colab_t4_gpu_aimd_workflow.md`](file:///home/yamazaki/mdi_workspace_backup/.agents/rules/colab_t4_gpu_aimd_workflow.md)
  - §3「SSH 接続」に追記（A の接続部分・C）
  - §1「Drive 同期」に追記（B）
  - §8「リアルタイム監視」に追記（D）
  - 新規 §9「Colab ランタイム再起動時の復旧・リスタート手順」を追加（A）
- `AGENTS.md` は §3 に 1 行の参照追記のみ（本文は重複させない）。
- 新規 Skill は作らない（手順は 1 ルール内の短いチェックリストで足りるため）。

## 3. 追記する具体的な文言（案）

### §1 に追加
```markdown
* **バックアップ先フォルダ名の実在確認**:
  * ユーザーが Drive 側でフォルダ名を変更することがある。同期ループを張る前に
    `ls -d /content/drive/MyDrive/MD_backup/*<周期数>周期*` で実フォルダ名を確認し、
    変更されていればそちらへ追従すること（古い名前に新規フォルダを作って分散させない）。
```

### §3 に追加
```markdown
* **コマンド実行の安全作法（WSL）**:
  * `sudo` を伴うコマンド（例: `mount -t drvfs`）は実行しない（パスワード待ちで固まる）。
  * SSH は常に `-o BatchMode=yes -o ConnectTimeout=10` を付ける。
  * WSL から Google Drive (`G:`) への書き込みは、`/mnt/c/temp_sic_sync/` に一旦コピーし
    `powershell.exe -Command "Copy-Item ..."` で `G:\マイドライブ\MD_backup\<フォルダ>\` へ転送する。
  * PowerShell の出力は文字化け・折り返しされるため、内容確認は Python で読み出すこと。
```

### §8 に追加
```markdown
4. **`stream_iteration.py` の必須仕様**:
   - `ssh -tt` と `stdbuf -oL tail -f` で行バッファを強制する。
   - 出力の無い反復計算中も、スピナーと経過秒を毎 0.5 秒更新するハートビートを表示する。
   - 監視対象パスは「現在走っている計算ディレクトリ」に合わせて更新する（引数での上書き可）。
```

### 新規 §9
```markdown
## 9. Colab ランタイム再起動時の復旧・リスタート手順
Colab は約 14 時間で停止する。再開時は次の順で実施し、既存の計算フォルダは上書きしない。
1. 新しい ngrok の `host:port` を `~/.ssh/config` と `<workspace>/.ssh/config` の両方に反映する。
2. `/opt/nvidia/hpc_sdk` が無ければ NVHPC 24.7 を再導入
   （`deb [trusted=yes] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /` → `apt-get install nvhpc-24-7`、約 5 分）。
   `pip install ase pymdi` と、Drive の `mdi_binaries/` → `/content/bin/` への再配置も行う。
3. Drive 上の `dump.lammpstrj` から最終フレームを抽出し、`slab_..._relaxed_stepNN.data` を作る
   （原子 ID でソート、Type1=C / Type2=Si）。
4. `calc_..._restart/` と Colab 側 `/content/..._MD_restart/`、Drive 側 `.../restart/` を新規作成し、
   `in.lammps`（`minimize 1.0e-6 1.0e-2 100 150`）、`run_colab_gpu.sh`、`master_run_gpu.sh` を配置して起動する。
   `run_colab_gpu.sh` の `rm -rf` に `nohup.out` を含めない。
5. 起動後、`nvidia-smi` で `pw.x.real` の VRAM 使用と Drive 同期ループを確認する。
```

## 4. 確認したい点
1. 上記 4 か所の追記と新規 §9 で進めてよいですか？
2. Colab の連続稼働制限を考慮し、「停止検知時に自動でこの手順を提案する」運用も入れますか？（入れない場合は現案のまま）
3. `AGENTS.md` への参照 1 行追記は不要ですか？
