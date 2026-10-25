import json

with open('/home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb', 'r') as f:
    nb = json.load(f)
    for i, cell in enumerate(nb['cells']):
        if 'source' in cell:
            src = ''.join(cell['source'])
            if 'configure' in src or 'cmake' in src or 'q-e' in src:
                print(f"--- Cell {i} ---")
                print(src)
