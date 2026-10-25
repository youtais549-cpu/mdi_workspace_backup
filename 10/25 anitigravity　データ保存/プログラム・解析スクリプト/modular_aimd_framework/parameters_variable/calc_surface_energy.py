#!/usr/bin/env python3
"""
表面破壊エネルギー (へき開エネルギー) 自動算出・統合データベース記録ツール
【ユーザー実行コマンド】
1. 完全自動モード (最新の計算結果から自動抽出・記録):
   python3 calc_surface_energy.py --auto
   または
   python3 calc_surface_energy.py --auto <slab_dir> <bulk_dir>

2. 手動数値指定モード:
   python3 calc_surface_energy.py <E_slab> <E_bulk> [slab_dir] [bulk_dir] [note]

fracture_metadata.json, model_settings.py, dft_settings.py から解析条件を自動取得し、
γ [J/m²] を算出して文献値 (Rauls et al. 1999) と比較した上で、
SURFACE_ENERGY_RESULTS.md および surface_energy_results.csv に自動追記します。
"""
import os
import sys
import glob
import json
import datetime
import importlib.util

RY_TO_EV = 13.6056980659

def load_settings():
    """解析条件 (DFT & Model) を自動ロード"""
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    model_settings_path = os.path.join(curr_dir, "model_settings.py")
    dft_settings_path = os.path.join(curr_dir, "dft_settings.py")
    meta_path = os.path.join(curr_dir, "fracture_metadata.json")

    settings = {
        'plane': '10-10',
        'n_periods': 2,
        'n_layers': 4,
        'natoms': 72,
        'vacuum': 10.0,
        'supercell_xy': [3, 3],
        'ecutwfc': 40.0,
        'ecutrho': 320.0,
        'kpts': 'gamma',
        'mode': 'CG_minimize (F <= 1.0e-3 eV/Å)',
        'area_2a': 279.4977
    }

    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            settings['area_2a'] = meta.get('total_area_2A_angstrom2', settings['area_2a'])
            settings['plane'] = meta.get('cleavage_plane', settings['plane'])
            settings['natoms'] = meta.get('natoms', settings['natoms'])
            settings['n_periods'] = meta.get('n_periods', settings['n_periods'])
            settings['n_layers'] = meta.get('n_layers', settings['n_layers'])
            settings['vacuum'] = meta.get('vacuum_thickness_angstrom', settings['vacuum'])
            settings['supercell_xy'] = meta.get('supercell_xy', settings['supercell_xy'])
        except Exception:
            pass

    if os.path.exists(dft_settings_path):
        try:
            spec = importlib.util.spec_from_file_location("dft_settings", dft_settings_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            cfg = getattr(mod, 'DFT_CONFIG', {})
            settings['ecutwfc'] = cfg.get('ecutwfc', settings['ecutwfc'])
            settings['ecutrho'] = cfg.get('ecutrho', settings['ecutrho'])
            k = cfg.get('kpts', None)
            settings['kpts'] = 'gamma' if k is None else str(k)
        except Exception:
            pass

    return settings

def extract_energy_from_dir(target_dir):
    """指定ディレクトリの出力ファイル (espresso.pwo または log.lammps) から全エネルギー [eV] を自動抽出"""
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {target_dir}")

    # 1. log.lammps の検索 (LAMMPS minimize ログ: eV単位)
    log_path = os.path.join(target_dir, "log.lammps")
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        in_thermo = False
        toteng_col = -1
        last_toteng = None
        for line in lines:
            parts = line.split()
            if 'TotEng' in parts:
                toteng_col = parts.index('TotEng')
                in_thermo = True
                continue
            if in_thermo:
                if len(parts) > toteng_col and parts[0].isdigit():
                    try:
                        last_toteng = float(parts[toteng_col])
                    except ValueError:
                        pass
                elif 'Loop time' in line or 'ERROR' in line or 'minimize' in line:
                    in_thermo = False
        if last_toteng is not None:
            return last_toteng

    # 2. espresso.pwo の検索 (Quantum ESPRESSO ログ: Ry単位 -> eV換算)
    pwo_path = os.path.join(target_dir, "espresso.pwo")
    if os.path.exists(pwo_path):
        with open(pwo_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for line in reversed(lines):
            if '!    total energy' in line:
                parts = line.split('=')[1].split()
                ry = float(parts[0])
                ev = ry * RY_TO_EV
                return ev

    raise ValueError(f"{target_dir} 内に有効な espresso.pwo または log.lammps が見つかりませんでした。")

def find_latest_calculation_dirs():
    """ワークスペース内の最新のスラブディレクトリとバルクディレクトリを自動検出"""
    base_dirs = [
        "/home/yamazaki/mdi_workspace_backup",
        os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")),
        "/content/drive/MyDrive/MD_backup"
    ]
    
    slab_dirs = []
    bulk_dirs = []
    for b in base_dirs:
        if os.path.exists(b):
            for d in glob.glob(os.path.join(b, "*slab*")):
                if os.path.isdir(d): slab_dirs.append(d)
            for d in glob.glob(os.path.join(b, "*bulk*")):
                if os.path.isdir(d): bulk_dirs.append(d)

    if not slab_dirs:
        raise FileNotFoundError("スラブ計算結果ディレクトリが見つかりませんでした。")
    if not bulk_dirs:
        raise FileNotFoundError("バルク計算結果ディレクトリが見つかりませんでした。")

    # 更新時刻順にソートして最新を取得
    slab_dirs.sort(key=os.path.getmtime, reverse=True)
    bulk_dirs.sort(key=os.path.getmtime, reverse=True)
    return slab_dirs[0], bulk_dirs[0]

def append_to_database(record):
    """SURFACE_ENERGY_RESULTS.md および surface_energy_results.csv に結果を追記"""
    root_dirs = [
        "/home/yamazaki/mdi_workspace_backup",
        os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")),
        "/content/drive/MyDrive/MD_backup"  # Colab環境
    ]
    
    target_root = None
    for r in root_dirs:
        if os.path.exists(r) and os.path.isdir(r):
            target_root = r
            break
            
    if not target_root:
        target_root = os.path.dirname(os.path.abspath(__file__))

    md_path = os.path.join(target_root, "SURFACE_ENERGY_RESULTS.md")
    csv_path = os.path.join(target_root, "surface_energy_results.csv")

    # 1. CSV に追記
    next_no = 1
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if len(lines) > 1:
                try:
                    last_line = lines[-1]
                    next_no = int(last_line.split(",")[0]) + 1
                except ValueError:
                    next_no = len(lines)
    else:
        header = "No,Date,Plane,Periods,Layers,Natoms,Vacuum_Angstrom,Supercell_XY,Mode,Ecutwfc_Ry,Ecutrho_Ry,Kpoints,E_slab_eV,E_bulk_eV,Delta_E_eV,Area_2A_Angstrom2,Gamma_J_m2,Ref_Relaxed_J_m2,Ref_Unrelaxed_J_m2,Diff_Relaxed_Percent,Archive_Slab,Archive_Bulk\n"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(header)

    already_exists = False
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            es_str = f"{record['e_slab']:.4f}"
            eb_str = f"{record['e_bulk']:.4f}"
            if es_str in content and eb_str in content:
                already_exists = True

    if already_exists:
        print(f"ℹ️ 本計算データ (E_slab={record['e_slab']:.4f}, E_bulk={record['e_bulk']:.4f}) は既にデータベースに登録されています。")
        return

    record['no'] = next_no
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    csv_row = (
        f"{next_no},{date_str},{record['plane']},{record['n_periods']},{record['n_layers']},"
        f"{record['natoms']},{record['vacuum']},{record['supercell_xy'][0]}x{record['supercell_xy'][1]},"
        f"\"{record['mode']}\",{record['ecutwfc']},{record['ecutrho']},{record['kpts']},"
        f"{record['e_slab']:.4f},{record['e_bulk']:.4f},{record['delta_e']:.4f},{record['area_2a']:.4f},"
        f"{record['gamma']:.4f},{record['ref_relaxed']},{record['ref_unrelaxed']},{record['diff_percent']:+.1f},"
        f"\"{record['archive_slab']}\",\"{record['archive_bulk']}\"\n"
    )
    with open(csv_path, "a", encoding="utf-8") as f:
        f.write(csv_row)

    # 2. Markdown 表に追記
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        md_row = (
            f"| **#{next_no:02d}** | {date_str} | {{{record['plane']}}} | {record['n_periods']}周期 ({record['n_layers']}層) | "
            f"{record['natoms']} | {record['vacuum']} | {record['supercell_xy'][0]}x{record['supercell_xy'][1]} | "
            f"{record['mode']} | {record['ecutwfc']} / {record['ecutrho']} | {record['kpts']} | "
            f"{record['e_slab']:,.4f} | {record['e_bulk']:,.4f} | {record['delta_e']:.4f} | "
            f"{record['area_2a']:.4f} | **{record['gamma']:.4f}** | "
            f"緩和後 {record['ref_relaxed']} ({record['diff_percent']:+.1f}%) | `{record['archive_slab']}`<br>`{record['archive_bulk']}` |\n"
        )

        if "| **#" in md_content:
            lines = md_content.splitlines()
            last_table_idx = -1
            for idx, line in enumerate(lines):
                if line.strip().startswith("| **#"):
                    last_table_idx = idx
            if last_table_idx != -1:
                lines.insert(last_table_idx + 1, md_row.strip())
                new_md_content = "\n".join(lines)
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(new_md_content)
        else:
            with open(md_path, "a", encoding="utf-8") as f:
                f.write("\n" + md_row)

    print(f"✅ 総合データベースへの自動追記が完了しました:")
    print(f"  - Markdown: {md_path}")
    print(f"  - CSV     : {csv_path}")

def calculate_gamma(e_slab, e_bulk, slab_dir="", bulk_dir="", note=""):
    settings = load_settings()
    area_2a = settings['area_2a']
    plane = settings['plane']
    natoms = settings['natoms']

    conv = 16.021766  # 1 eV/Å² -> J/m²
    delta_e = e_slab - e_bulk
    gamma = (delta_e / area_2a) * conv

    ref_relaxed = 2.27
    ref_unrelaxed = 2.44
    diff_percent = ((gamma - ref_relaxed) / ref_relaxed) * 100.0

    print("\n==================================================")
    print(" 表面破壊エネルギー (γ) 算出結果レポート")
    print("==================================================")
    print(f"対象モデル        : 2H-SiC {{{plane}}} 面 ({natoms} 原子)")
    print(f"スラブ全エネルギー E_slab : {e_slab:.6f} eV")
    print(f"バルク全エネルギー E_bulk : {e_bulk:.6f} eV")
    print(f"過剰エネルギー     ΔE     : {delta_e:.6f} eV")
    print(f"全破面表面積       2A     : {area_2a:.4f} Å²")
    print("--------------------------------------------------")
    print(f"表面破壊エネルギー γ     : {gamma:.4f} J/m²")
    print("--------------------------------------------------")

    if plane == '10-10':
        print("【文献値との比較 (Rauls et al., Solid State Commun. 1999)】")
        print(f"  ・非緩和 (切断直後)   : {ref_unrelaxed} J/m²")
        print(f"  ・表面構造緩和後     : {ref_relaxed} J/m² (差分: {diff_percent:+.1f}%)")
        diff = abs(gamma - ref_relaxed)
        if diff < 0.2:
            print("  ✅ 判定: 緩和後の文献値と極めて高い一致度を示しています！")
        elif diff < 0.5:
            print("  良好: 文献値の許容範囲内に収まっています。")
        else:
            print("  ⚠️ 注意: 文献値から乖離があります。スラブ層数や収束度を確認してください。")
    print("==================================================\n")

    record = {
        'e_slab': e_slab,
        'e_bulk': e_bulk,
        'delta_e': delta_e,
        'area_2a': area_2a,
        'gamma': gamma,
        'plane': plane,
        'natoms': natoms,
        'n_periods': settings['n_periods'],
        'n_layers': settings['n_layers'],
        'vacuum': settings['vacuum'],
        'supercell_xy': settings['supercell_xy'],
        'ecutwfc': settings['ecutwfc'],
        'ecutrho': settings['ecutrho'],
        'kpts': settings['kpts'],
        'mode': settings['mode'],
        'ref_relaxed': ref_relaxed,
        'ref_unrelaxed': ref_unrelaxed,
        'diff_percent': diff_percent,
        'archive_slab': os.path.basename(slab_dir) if slab_dir else "results_2H-SiC_10-10_slab_relaxed_20261020",
        'archive_bulk': os.path.basename(bulk_dir) if bulk_dir else "2H-SiC_10-10_bulk_scf_20261020",
        'note': note
    }

    append_to_database(record)
    return gamma

def auto_evaluate(slab_dir=None, bulk_dir=None):
    """ディレクトリからエネルギーを自動抽出して評価"""
    if not slab_dir or not bulk_dir:
        slab_dir, bulk_dir = find_latest_calculation_dirs()

    print(f"🔍 自動評価モードを実行中...")
    print(f"  スラブディレクトリ: {slab_dir}")
    print(f"  バルクディレクトリ: {bulk_dir}")

    e_slab = extract_energy_from_dir(slab_dir)
    e_bulk = extract_energy_from_dir(bulk_dir)
    return calculate_gamma(e_slab, e_bulk, slab_dir, bulk_dir, note="Auto evaluated")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        s_dir = sys.argv[2] if len(sys.argv) >= 3 else None
        b_dir = sys.argv[3] if len(sys.argv) >= 4 else None
        auto_evaluate(s_dir, b_dir)
    elif len(sys.argv) >= 3:
        try:
            es = float(sys.argv[1])
            eb = float(sys.argv[2])
            s_dir = sys.argv[3] if len(sys.argv) >= 4 else ""
            b_dir = sys.argv[4] if len(sys.argv) >= 5 else ""
            n = sys.argv[5] if len(sys.argv) >= 6 else ""
            calculate_gamma(es, eb, s_dir, b_dir, n)
        except ValueError:
            print("引数エラー: エネルギー数値を指定してください。")
    else:
        # デフォルトで最新結果の自動検出・評価を実行
        try:
            auto_evaluate()
        except Exception as e:
            print(f"自動検出エラー: {e}")
            print("手動で数値を入力してください:")
            try:
                es = float(input("スラブ全エネルギー E_slab [eV] を入力してください: "))
                eb = float(input("バルク全エネルギー E_bulk [eV] を入力してください: "))
                calculate_gamma(es, eb)
            except (ValueError, KeyboardInterrupt):
                print("\n入力をキャンセルしました。")
