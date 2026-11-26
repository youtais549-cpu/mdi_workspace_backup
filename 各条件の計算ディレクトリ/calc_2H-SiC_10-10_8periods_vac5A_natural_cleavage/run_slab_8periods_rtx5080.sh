#!/bin/bash
# ==============================================================================
# run_slab_8periods_rtx5080.sh
# ローカル新環境 (Core Ultra 9 285K 24コア / RAM 64GB / RTX 5080 16GB) 上で
# 2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 5.0 Å 自然へき開面スラブモデルの
# LAMMPS (DRIVER) + Quantum ESPRESSO (MDI ENGINE) 連成構造緩和を実行するスクリプト
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_PREFIX="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
if [ -d "$ENV_PREFIX/bin" ]; then
    export PATH="$SCRIPT_DIR/bin:$ENV_PREFIX/bin:$PATH"
    export LD_LIBRARY_PATH="$ENV_PREFIX/lib:${LD_LIBRARY_PATH:-}"
fi

export OMPI_MCA_btl_vader_single_copy_mechanism=none
export QE_MPI_NP=${QE_MPI_NP:-12}
export QE_OMP_THREADS=${QE_OMP_THREADS:-2}

# 新規出力ファイル初期化 (既存他ディレクトリのファイルは一切触らない)
rm -rf tmp espresso.pwo espresso_all_steps.pwo dump.lammpstrj qe_engine.log lmp.log log.lammps

LMP_BIN="$ENV_PREFIX/bin/lmp"
if [ ! -x "$LMP_BIN" ]; then
    LMP_BIN="$(which lmp 2>/dev/null || true)"
fi

if [ -z "$LMP_BIN" ] || [ ! -x "$LMP_BIN" ]; then
    echo "❌ エラー: LAMMPS (lmp) が見つかりません。"
    exit 1
fi

MDI_PORT=${MDI_PORT:-8028}

echo "============================================================"
echo " Starting LAMMPS + QE MDI 8-Period Slab Relaxation"
echo " Environment : Core Ultra 9 285K (24 cores) / RAM 64GB / RTX 5080 16GB"
echo " Model       : 2H-SiC {10-10} 8-Periods (16 layers, 288 atoms), Vacuum 5.0 Å"
echo " Convergence : minimize 1.0e-6 1.0e-2 100 150 (AGENTS.md §9)"
echo " Parallelism : MPI_NP=$QE_MPI_NP x OMP_NUM_THREADS=$QE_OMP_THREADS (24 threads)"
echo " LAMMPS Bin  : $LMP_BIN | TCP Port: $MDI_PORT"
echo "============================================================"

# 1. LAMMPS を MDI DRIVER としてバックグラウンド起動
echo "1. Starting LAMMPS MDI driver..."
"$LMP_BIN" -mdi "-role DRIVER -name LAMMPS -method TCP -port $MDI_PORT" -in in.lammps > lmp.log 2>&1 &
LMP_PID=$!

sleep 1

# 2. Python QE MDI Engine を起動
echo "2. Starting Python QE MDI engine..."
python3 qe_mdi_engine_rtx5080.py -mdi "-role ENGINE -name QE -method TCP -port $MDI_PORT -hostname localhost" > qe_engine.log 2>&1

# 3. LAMMPS 完了待機
wait $LMP_PID

echo "============================================================"
echo " Calculation Completed Successfully!"
echo " 3. Converting trajectory to Winmostar XYZ format (sorted by Atom ID)..."
python3 make_xyz.py dump.lammpstrj md_animation.xyz

# 4. 指示書 (RELAXATION_GRAPH_PROTOCOL.json) に基づく3種推移グラフの自動生成 (AGENTS.md §8)
echo " 4. Generating 3 progression graphs according to protocol..."
python3 auto_generate_progression_graphs.py

# 5. 表面破壊エネルギー γ の自動算出とメタデータ更新
echo " 5. Evaluating 8-Period Surface Fracture Energy γ..."
python3 - << 'PY_EOF'
import json, re, os

with open("fracture_metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

e_bulk = meta["true_bulk_scf_energy_eV"]
e_bulk_ry = meta["true_bulk_scf_energy_Ry"]
denom = meta["effective_denominator"]
ref_relaxed = meta.get("reference_rauls_relaxed_J_m2", 2.27)
ref_unrelaxed = meta.get("reference_rauls_unrelaxed_J_m2", 2.44)
ref_dimer = meta.get("reference_rauls_dimer_J_m2", 3.03)

energies_qe = []
if os.path.exists("qe_engine.log"):
    with open("qe_engine.log", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r"Total Energy:\s+([-\d\.]+)\s+eV", line)
            if m:
                energies_qe.append(float(m.group(1)))

energies_lmp = []
if os.path.exists("log.lammps"):
    with open("log.lammps", "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    m_fin = re.search(r"Energy initial, next-to-last, final =\s*\n\s*([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)", text)
    if m_fin:
        energies_lmp.append(float(m_fin.group(3)))

ry_slab_list = []
if os.path.exists("espresso.pwo"):
    with open("espresso.pwo", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "!    total energy" in line:
                ry_slab_list.append(float(line.split("=")[1].split()[0]))

if energies_qe or energies_lmp:
    e_slab = energies_lmp[-1] if energies_lmp else energies_qe[-1]
    e_slab_qe = energies_qe[-1] if energies_qe else e_slab
    ry_slab = ry_slab_list[-1] if ry_slab_list else None
    delta_e = e_slab - e_bulk
    gamma = delta_e / denom
    diff_pct = ((gamma - ref_relaxed) / ref_relaxed) * 100.0

    meta["relaxed_slab_energy_eV"] = round(e_slab, 4)
    meta["relaxed_slab_energy_qe_eV"] = round(e_slab_qe, 4)
    if ry_slab is not None:
        meta["relaxed_slab_energy_Ry"] = round(ry_slab, 8)
    meta["delta_energy_eV"] = round(delta_e, 4)
    meta["surface_fracture_energy_J_m2"] = round(gamma, 4)
    meta["diff_percent"] = round(diff_pct, 1)

    with open("fracture_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    print("------------------------------------------------------------")
    print(f"  [8周期 (16層, 288原子) 表面破壊エネルギー算出結果]")
    print(f"  - E_bulk (288 atoms) : {e_bulk:.4f} eV ({e_bulk_ry:.8f} Ry)")
    print(f"  - E_slab (relaxed)   : {e_slab:.4f} eV (QE: {e_slab_qe:.4f} eV)")
    print(f"  - ΔE = E_slab-E_bulk : {delta_e:.4f} eV")
    print(f"  - 全破面積 2A        : {meta['total_area_2A_angstrom2']:.4f} Å²")
    print(f"  - 表面破壊エネルギー γ: {gamma:.4f} J/m²")
    print(f"  - 文献値比較 (Rauls 1999 緩和後 2.27 J/m²): {diff_pct:+.1f}%")
    print(f"  - 文献値比較 (Rauls 1999 実測/ダイマー 3.03 J/m²)")
    print("------------------------------------------------------------")
PY_EOF

echo " Done!"
echo "============================================================"

