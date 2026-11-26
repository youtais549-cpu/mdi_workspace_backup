#!/bin/bash
# ==============================================================================
# run_slab_rtx5080.sh
# ローカル新環境 (Core Ultra 9 285K / RAM 64GB / RTX 5080 16GB) 上で
# LAMMPS (DRIVER) + Quantum ESPRESSO (MDI ENGINE) 連成構造緩和を実行するスクリプト
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ローカル Python 仮想環境があれば有効化
ENV_PREFIX="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
if [ -d "$ENV_PREFIX/bin" ]; then
    export PATH="$SCRIPT_DIR/bin:$ENV_PREFIX/bin:$PATH"
    export LD_LIBRARY_PATH="$ENV_PREFIX/lib:${LD_LIBRARY_PATH:-}"
elif [ -f "$HOME/.venvs/mdi_rtx5080/bin/activate" ]; then
    source "$HOME/.venvs/mdi_rtx5080/bin/activate"
fi

# 実行前の新規出力ファイル初期化 (既存フォルダのファイルは一切触らない)
rm -rf tmp espresso.pwo espresso_all_steps.pwo dump.lammpstrj qe_engine.log lmp.log log.lammps

# LAMMPS バイナリの自動検出
LMP_BIN=""
for cand in "$SCRIPT_DIR/bin/lmp" "$HOME/.local/bin/lmp" "/usr/local/bin/lmp" "$(which lmp 2>/dev/null || true)" "$(which lmp_mpi 2>/dev/null || true)"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then
        LMP_BIN="$cand"
        break
    fi
done

if [ -z "$LMP_BIN" ]; then
    echo "❌ エラー: LAMMPS (lmp) が見つかりません。先に 'bash setup_local_rtx5080_env.sh' を実行してください。"
    exit 1
fi

MDI_PORT=${MDI_PORT:-8021}

echo "============================================================"
echo " Starting LAMMPS + QE MDI Slab Relaxation (RTX 5080 / Ultra 9 285K)"
echo " Model: 2H-SiC {10-10} 2-Periods (72 atoms), Vacuum 5.0 Å"
echo " Convergence Standard: minimize 1.0e-6 1.0e-2 100 150"
echo " LAMMPS Binary: $LMP_BIN | TCP Port: $MDI_PORT"
echo "============================================================"

# 1. LAMMPS を MDI DRIVER としてバックグラウンド起動
echo "1. Starting LAMMPS MDI driver..."
"$LMP_BIN" -mdi "-role DRIVER -name LAMMPS -method TCP -port $MDI_PORT" -in in.lammps > lmp.log 2>&1 &
LMP_PID=$!

sleep 1

# 2. Python QE MDI Engine (RTX 5080 / Ultra 9 285K 対応版) を起動
echo "2. Starting Python QE MDI engine (RTX 5080)..."
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

# 5. 表面破壊エネルギー γ の自動算出と T4 GPU 結果との整合性検証
echo " 5. Evaluating Surface Fracture Energy γ..."
python3 - << 'PY_EOF'
import json, re, os

with open("fracture_metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

e_bulk = meta["true_bulk_scf_energy_eV"]
denom = meta["effective_denominator"]
ref_t4_gamma = meta["reference_t4_surface_fracture_energy_J_m2"]
ref_lit_gamma = meta["reference_rauls_dimer_J_m2"]

energies = []
if os.path.exists("qe_engine.log"):
    with open("qe_engine.log", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r"Total Energy:\s+([-\d\.]+)\s+eV", line)
            if m:
                energies.append(float(m.group(1)))

if energies:
    e_slab = energies[-1]
    delta_e = e_slab - e_bulk
    gamma = delta_e / denom
    diff_t4 = abs(gamma - ref_t4_gamma)
    meta["rtx5080_relaxed_slab_energy_eV"] = round(e_slab, 4)
    meta["rtx5080_delta_energy_eV"] = round(delta_e, 4)
    meta["rtx5080_surface_fracture_energy_J_m2"] = round(gamma, 4)
    with open("fracture_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)
    print("------------------------------------------------------------")
    print(f"  [RTX 5080 計算結果検証サマリー]")
    print(f"  - E_bulk (72 atoms) : {e_bulk:.4f} eV")
    print(f"  - E_slab (relaxed)  : {e_slab:.4f} eV")
    print(f"  - ΔE = E_slab-E_bulk: {delta_e:.4f} eV")
    print(f"  - 表面破壊エネルギー γ: {gamma:.4f} J/m²")
    print(f"  - 旧環境 (T4 GPU) 値 : {ref_t4_gamma:.4f} J/m² (差分: {diff_t4:.4f} J/m²)")
    print(f"  - 文献値 (Rauls 1999): {ref_lit_gamma:.2f} J/m²")
    print("------------------------------------------------------------")
PY_EOF

echo " Done!"
echo "============================================================"

