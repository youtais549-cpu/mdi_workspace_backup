# パソコン修理後のデータ復元マニュアル (Restore Instructions)

パソコンの修理が完了し、新しい環境が整ったら以下の手順でデータを元の状態に復元してください。

## 1. プログラムとスクリプトの復元
1. 新しいパソコンでターミナル（またはAntigravity IDE）を開きます。
2. 以下のコマンドを実行して、GitHubからバックアップデータをダウンロードします。
   ```bash
   git clone https://github.com/youtais549-cpu/mdi_workspace_backup.git
   ```
3. ダウンロードされた `mdi_workspace_backup` フォルダの中に、元のプログラムファイルが全て入っています。

## 2. Python (Conda) 環境の復元
計算に必要な `pymdi` などのパッケージを元通りにします。
1. Minicondaをインストールします。
2. ダウンロードしたフォルダ内にある設定ファイルを使って、環境を復元します。
   ```bash
   cd mdi_workspace_backup
   conda env create -f conda_environment.yml
   ```
   ※もしOS環境の違いでエラーが出る場合は、同梱されている `conda_requirements.txt` を見ながら `pip install pymdi` 等を行ってください。

## 3. Zoteroデータの復元 (文献情報とPDF)
1. 新しいパソコン（Windows）に Zotero をインストールし、一度起動してから完全に閉じます。
2. ダウンロードしたフォルダ内にある `Zotero_backup` フォルダの中身をすべてコピーします。
3. Windowsのエクスプローラーで `C:\Users\yamazaki yuta\Zotero` を開き、中身を上書き保存（ペースト）します。
   （これで文献もPDFも完全に元通りになります）

## 4. SSH鍵と計算結果の復元 (Googleドライブ・USBから)
Googleドライブ等に避難させた `PC_Repair_Backup.tar.gz` を活用します。
1. Windows上で `PC_Repair_Backup.tar.gz` を解凍します。
2. 中に入っている `.ssh` フォルダを、新しい環境の `/home/yamazaki_yuta/.ssh/` に配置します。（これで外部サーバーやColabへの接続が復活します）
3. 巨大な計算結果（`.lammpstrj`, `.dump` など）もこの中にまとまっていますので、必要に応じてワークスペースに戻してください。

## 5. LAMMPS / Quantum ESPRESSO の再ビルド
ソフトウェア自体はバックアップされていないため、再インストールが必要です。
1. LAMMPSをビルドする際の設定は、リポジトリ内の `lammps_CMakeCache_backup.txt` をカンペとして参考にしてください。
2. Antigravity IDEに「PCが直ったのでQEとLAMMPSをビルドして」と指示を出せば、自動でサポートを行います。

---
以上で復元は完了です。お疲れ様でした！
