import sys
import py3Dmol

if len(sys.argv) < 2:
    print("使い方: python cif_viewer.py <cifファイル名>")
    sys.exit(1)

cif_file = sys.argv[1]
with open(cif_file, 'r') as f:
    cif_data = f.read()

view = py3Dmol.view(width=800, height=600)
view.addModel(cif_data, "cif")
view.setStyle({'stick': {}, 'sphere': {'radius': 0.3}})
view.zoomTo()

html_code = view._make_html()

html_file = cif_file + ".html"
with open(html_file, 'w') as f:
    f.write(html_code)

print(f"作成完了: {html_file}")
print("左側のエクスプローラーからこのファイルをクリックして開くと、3Dモデルが見られます！")
