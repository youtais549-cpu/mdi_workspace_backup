#!/bin/bash
# ==============================================================================
# run_bulk_8periods_rtx5080.sh
# 2H-SiC {10-10} 8周期 (16層, 288原子) 真のバルクモデル (真空 0 Å)
# Quantum ESPRESSO 1点 SCF 計算実行 & エネルギー自動検証スクリプト
# 【AGENTS.md §1 準拠: スラブ緩和前の「バルク 1 点 SCF 先行確定」プロトコル】
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

# 環境パスの設定
ENV_PREFIX="/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
export PATH="$ENV_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$ENV_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_MAXSIZE=2147483648

# 擬ポテンシャルファイルの配置確認
if [ ! -f "C.upf" ]; then
    cp "$WORKSPACE_DIR/calc_2H-SiC_10-10_6periods_true_bulk_scf/C.upf" ./
fi
if [ ! -f "Si.upf" ]; then
    cp "$WORKSPACE_DIR/calc_2H-SiC_10-10_6periods_true_bulk_scf/Si.upf" ./
fi

# モデルと入力ファイルが未生成なら自動生成
if [ ! -f "espresso.pwi" ]; then
    python3 create_8periods_bulk_and_slab_models.py
fi

PW_BIN="$ENV_PREFIX/bin/pw.x"
MPI_NP=${QE_MPI_NP:-12}
export OMP_NUM_THREADS=${QE_OMP_THREADS:-2}

echo "============================================================"
echo " Starting 8-Periods (288 atoms) True Bulk 1-Point SCF"
echo " Hardware : Core Ultra 9 285K (24 cores) / RAM 64GB / RTX 5080 16GB"
echo " Parallel : MPI_NP=$MPI_NP x OMP_NUM_THREADS=$OMP_NUM_THREADS (Total 24 threads)"
echo "============================================================"
nvidia-smi --query-gpu=name,driver_version,memory.total,temperature.gpu,power.draw --format=csv || true

mkdir -p tmp
T0=$(date +%s)

mpirun --oversubscribe -np "$MPI_NP" "$PW_BIN" -ndiag 1 < espresso.pwi > espresso.pwo 2>&1

T1=$(date +%s)
ELAPSED=$((T1 - T0))

echo "============================================================"
echo " 8-Periods (288 atoms) True Bulk SCF Finished in ${ELAPSED}s!"
grep -E "(!    total energy|Total force)" espresso.pwo || true
echo "============================================================"

# fracture_metadata.json への自動記録と 1原子あたりエネルギーの整合性検証 (AGENTS.md §1)
python3 - << 'PY_EOF'
import json, re

with open("espresso.pwo", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

m_e = re.findall(r"!\s+total energy\s+=\s+([-\d\.]+)\s+Ry", text)
m_f = re.findall(r"Total force\s+=\s+([-\d\.]+)\s+Total SCF correction\s+=\s+([-\d\.]+)", text)

if m_e:
    e_ry = float(m_e[-1])
    # QE -> eV 換算 (1 Ry = 13.605693122994 eV, 6周期と同基準の 13.6056980659 も併記)
    # 過去台帳 (72原子: -2347.20460935 Ry -> -31935.3562 eV => 換算係数 13.60569758)
    conv_ry_to_ev = 13.605693122994
    e_ev = e_ry * conv_ry_to_ev
    e_per_atom = e_ev / 288.0

    with open("fracture_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["true_bulk_scf_energy_Ry"] = round(e_ry, 8)
    meta["true_bulk_scf_energy_eV"] = round(e_ev, 4)
    meta["energy_per_atom_eV"] = round(e_per_atom, 6)
    if m_f:
        meta["total_force_Ry_au"] = float(m_f[-1][0])
        meta["total_scf_correction_Ry_au"] = float(m_f[-1][1])

    with open("fracture_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    print("------------------------------------------------------------")
    print(" [8周期 (288原子) 真のバルク SCF 検証結果]")
    print(f"  - 全エネルギー E_bulk (Ry) : {e_ry:.8f} Ry")
    print(f"  - 全エネルギー E_bulk (eV) : {e_ev:.4f} eV")
    print(f"  - 1原子あたりエネルギー    : {e_per_atom:.4f} eV/atom (基準: -443.55 eV/atom)")
    print(f"  - 2周期 (72原子) の4倍比   : {-2347.20460730 * 4:.8f} Ry (差分: {e_ry - (-2347.20460730 * 4):.6f} Ry)")
    if m_f:
        print(f"  - Total force              : {m_f[-1][0]} Ry/au")
    print("  -> fracture_metadata.json に確定値を記録しました。")
    print("------------------------------------------------------------")
PY_EOF

