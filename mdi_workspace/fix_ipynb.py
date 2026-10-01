import json

filepath = "/home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb"
with open(filepath, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        for i, line in enumerate(source):
            if "--with-cuda-cc=75" in line:
                source[i] = line.replace("--with-cuda-cc=75", "--with-cuda-cc=80")
            if "if [ ! -f /content/drive/MyDrive/mdi_binaries/pw.x ]; then" in line:
                # We need to add rm -f before this, or just replace it
                pass
        
        # Let's do a simpler text replace on the whole source string list
        text = "".join(source)
        if "--with-cuda-cc=75" in text:
            text = text.replace("--with-cuda-cc=75", "--with-cuda-cc=80")
            text = text.replace("mkdir -p /content/drive/MyDrive/mdi_binaries", 
                                "mkdir -p /content/drive/MyDrive/mdi_binaries\nrm -f /content/drive/MyDrive/mdi_binaries/pw.x  # Force recompile for A100")
            
            # Write back to list
            lines = []
            for t in text.split("\n"):
                lines.append(t + "\n")
            # Remove trailing newline on last element
            if lines:
                lines[-1] = lines[-1].rstrip("\n")
            cell["source"] = lines

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Notebook updated!")
