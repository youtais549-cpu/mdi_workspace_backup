import json

with open('/home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb', 'r') as f:
    notebook = json.load(f)

for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        for i, line in enumerate(source):
            if "ZIPを解凍" in line:
                source[i] = "# 準備ができたら、以下のようにtar.gzを解凍して run_colab.sh を実行します。\n"
            elif "unzip" in line:
                source[i] = "# tar -xzvf /content/drive/MyDrive/colab_transfer.tar.gz -C /content/\n"
            elif "MD_Workspace/SiC_3x3x10_MD" in line:
                source[i] = "# cd /content/SiC_3x3x10_MD\n"

with open('/home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)
