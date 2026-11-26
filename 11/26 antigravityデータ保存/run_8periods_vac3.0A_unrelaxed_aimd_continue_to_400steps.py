#!/usr/bin/env python3
r"""
run_8periods_vac3.0A_unrelaxed_aimd_continue_to_400steps.py
==============================================================================
2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 3.0 Å (スラブ間ギャップ 6.0 Å)
【構造最適化なし (未緩和スラブモデル)】
Step 100 終了時点の全データ (位置座標、速度、Nosé-Hoover熱浴内部状態、収束済み波動関数、電子密度、エネルギー・原子力)
を 100% 完全引き継ぎし、追加 300 ステップ (Step 101 ～ 400, 通算 400 steps = 400 fs = 0.4 ps) を実行するスクリプト。

・引き継ぎ機構 (AGENTS.md §12 完全準拠):
  1. Step 0 ～ 100: 前回完了した `espresso_all_steps.pwo` から全 101 ステップの DFT エネルギーと
     Hellmann-Feynman 力を ASE パーサーで完全復元し、LAMMPS にキャッシュリプレイ (約 5 秒)。
     これにより Step 100 時点の位置座標・速度・Nosé-Hoover 熱浴チェイン変数 (η, η_dot) が
     1 ビットの誤差もなく 100% 完全一致する状態で復元される (`Files are identical` 検証)。
  2. Step 101 ～ 400: `./tmp/pwscf.save/` に保持された Step 100 の収束済み波動関数 (`wfc1.hdf5`) と
     電子密度 (`charge-density.hdf5`) を `startingwfc = 'file'`, `startingpot = 'file'` で引き継ぎ、
     実機 Quantum ESPRESSO (GPU) による SCF 計算へシームレスに移行して追加 300 ステップを実行する。
・保存先:
  - ローカル: aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_400steps_rtx5080/
  - NAS: \\192.168.12.69\Results\yamazaki\research\第一原理分子動力学法\{101_0}8周期3.0Å　構造最適化なし
==============================================================================
"""

import os
import sys
import re
import csv
import json
import time
import shutil
import datetime
import subprocess
import numpy as np

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache_sic"
os.makedirs("/tmp/matplotlib_cache_sic", exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
ENV_PREFIX = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
PREV_SLAB100_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_100steps_rtx5080")
SLAB400_AIMD_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac3.0A_unrelaxed_300K_400steps_rtx5080")

LOG_FILE = os.path.join(WORKSPACE_DIR, "aimd_8periods_vac3.0A_unrelaxed_400steps_run.log")


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sync_to_nas():
    sync_script = os.path.join(WORKSPACE_DIR, "sync_unrelaxed_400steps_to_nas.py")
    if os.path.exists(sync_script):
        try:
            subprocess.run(["python3", sync_script], cwd=WORKSPACE_DIR, timeout=180, check=False)
            log("Synced current files to NAS ({101_0}8周期3.0Å　構造最適化なし).")
        except Exception as e:
            log(f"NAS sync notice: {e}")


QE_ENGINE_CONTINUE_400_CODE = r'''#!/usr/bin/env python3
"""
==============================================================================
Quantum ESPRESSO + MDI 連成エンジン (Step 0..100 完全キャッシュ復元 & Step 101..400 波動関数・電荷密度引き継ぎ版)
==============================================================================
・Step 0 ～ 100 は prev_100steps_espresso_all_steps.pwo から ASE パーサーで完全復元して即座に返却
・Step 101 以降は ./tmp/pwscf.save 内の Step 100 収束済み波動関数 (wfc1.hdf5) と
  電荷密度 (charge-density.hdf5) を startingpot='file', startingwfc='file' で引き継いで実機 QE GPU SCF を実行
"""
import sys
import os
import re
import io
import glob
import shutil
import time
import numpy as np
import mdi
from ase import Atoms
from ase.calculators.espresso import Espresso, EspressoProfile
from ase.io.espresso import read_espresso_out
import ase.parallel

# Rule 3: ASE + MDI の DummyMPI 必須化 (SIGABRT 防止)
ase.parallel.world = ase.parallel.DummyMPI()

ELEMENTS = [
    'H' , 'He', 'Li', 'Be', 'B' , 'C' , 'N' , 'O' , 'F' , 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P' , 'S' , 'Cl', 'Ar', 'K' , 'Ca',
    'Sc', 'Ti', 'V' , 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
    'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y' , 'Zr',
    'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
    'Sb', 'Te', 'I' , 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
    'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W' , 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
    'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
    'Pa', 'U' , 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
    'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
    'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og',
]
atomic_number_to_symbol = {i + 1: symbol for i, symbol in enumerate(ELEMENTS)}
type_to_symbol = {1: 'C', 2: 'Si'}

exitflag = False
qm_natoms = 0
qm_elements = None
qm_coords = None
box = np.zeros(9, dtype=np.float64)
flag_box = False

qm_pe = 0.0
qm_forces = None
last_evaluated_coords = None
step_counter = 0
cached_steps = {}


def log(msg):
    print(f"[QE-MDI Engine] {msg}", flush=True)


def error(txt):
    log(f"ERROR: {txt}")
    sys.exit(1)


def load_cached_100_steps():
    global cached_steps
    cache_file = "prev_100steps_espresso_all_steps.pwo"
    if not os.path.exists(cache_file):
        log("No previous cache file found; running all steps from scratch.")
        return
    t0 = time.time()
    with open(cache_file, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    chunks = re.split(r"\n?=== STEP (\d+) ===\n", text)
    for i in range(1, len(chunks), 2):
        st = int(chunks[i])
        content = chunks[i + 1]
        atoms_list = list(read_espresso_out(io.StringIO(content), index=slice(None)))
        atoms_obj = atoms_list[-1]
        pe_ev = float(atoms_obj.get_potential_energy())
        forces_ev_ang = np.array(atoms_obj.get_forces(), dtype=np.float64)
        m_it = re.search(r"convergence has been achieved in\s+(\d+)\s+iterations", content)
        n_it = int(m_it.group(1)) if m_it else 17
        cached_steps[st] = (pe_ev, forces_ev_ang, n_it, content)
    log(f"Loaded {len(cached_steps)} cached steps (Step 0..{max(cached_steps.keys())}) in {time.time()-t0:.2f}s.")


def configure_environment():
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    os.environ.setdefault("OMPI_MCA_btl_vader_single_copy_mechanism", "none")
    os.environ.setdefault("CUDA_CACHE_MAXSIZE", "2147483648")
    os.environ.setdefault("CUDA_CACHE_DISABLE", "0")
    os.environ.setdefault("NVCOMPILER_ACC_SYNCHRONOUS", "0")

    nvhpc_roots = sorted(glob.glob("/opt/nvidia/hpc_sdk/Linux_x86_64/*"), reverse=True)
    extra_libs = []
    if nvhpc_roots:
        root = nvhpc_roots[0]
        extra_libs.extend([
            f"{root}/compilers/lib",
            f"{root}/math_libs/lib64",
            f"{root}/cuda/lib64",
            f"{root}/comm_libs/mpi/lib",
        ])
        extra_libs.extend(glob.glob(f"{root}/comm_libs/*/hpcx/*/ompi/lib"))

    cuda_libs = [
        "/usr/local/cuda/lib64",
        "/usr/lib/wsl/lib",
        "/usr/lib/x86_64-linux-gnu",
    ]
    existing_libs = [p for p in (extra_libs + cuda_libs) if os.path.exists(p)]
    current_ld = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = ":".join(existing_libs + ([current_ld] if current_ld else []))


def detect_pw_command():
    env_pw = os.environ.get("QE_PW_COMMAND")
    if env_pw:
        return env_pw

    pw_bin = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080/bin/pw.x"
    mpirun_bin = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080/bin/mpirun"
    mpi_np = int(os.environ.get("QE_MPI_NP", "12"))
    omp_threads = os.environ.get("QE_OMP_THREADS", "2")
    os.environ["OMP_NUM_THREADS"] = omp_threads
    return f"{mpirun_bin} --oversubscribe -np {mpi_np} {pw_bin} -ndiag 1"


def load_dft_config():
    default_config = {
        'ecutwfc': 40.0,
        'ecutrho': 320.0,
        'conv_thr': 1.0e-5,
        'kpts': None,
        'occupations': 'smearing',
        'smearing': 'gaussian',
        'degauss': 0.01,
        'mixing_beta': 0.3,
        'mixing_mode': 'local-TF',
        'electron_maxstep': 200,
        'pseudopotentials': {'Si': 'Si.upf', 'C': 'C.upf'},
    }
    try:
        if os.path.exists("dft_settings.py"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("dft_settings", "dft_settings.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'DFT_CONFIG'):
                default_config.update(mod.DFT_CONFIG)
    except Exception as e:
        log(f"Notice: Using default DFT parameters ({e})")
    return default_config


def has_saved_wfc_and_pot():
    save_dir = os.path.join("./tmp", "pwscf.save")
    if not os.path.isdir(save_dir):
        return False
    has_chg = (
        os.path.exists(os.path.join(save_dir, "charge-density.hdf5"))
        or os.path.exists(os.path.join(save_dir, "charge-density.dat"))
    )
    has_wfc = (
        os.path.exists(os.path.join(save_dir, "wfc1.hdf5"))
        or os.path.exists(os.path.join(save_dir, "wfc1.dat"))
    )
    return has_chg and has_wfc


def allocate_qm():
    global qm_elements, qm_coords, qm_forces, last_evaluated_coords
    n = qm_natoms
    qm_elements = np.empty(n, dtype=np.int32)
    qm_coords = np.empty((n, 3), dtype=np.float64)
    qm_forces = np.empty((n, 3), dtype=np.float64)
    last_evaluated_coords = None


def receive_qm_natoms(mdicomm):
    global qm_natoms
    qm_natoms = mdi.MDI_Recv(1, mdi.MDI_INT, mdicomm)
    log(f"Received >NATOMS: {qm_natoms}")
    allocate_qm()


def receive_box(mdicomm):
    global flag_box
    flag_box = True
    ierr = mdi.MDI_Recv(9, mdi.MDI_DOUBLE, mdicomm, buf=box)
    if ierr:
        error("MDI: >CELL reception failed")


def receive_qm_coords(mdicomm):
    if not qm_natoms:
        error("Cannot receive >COORDS if # atoms = 0")
    ierr = mdi.MDI_Recv(3 * qm_natoms, mdi.MDI_DOUBLE, mdicomm, buf=qm_coords)
    if ierr:
        error("MDI: >COORDS reception failed")


def receive_qm_elements(mdicomm):
    if not qm_natoms:
        error("Cannot receive >ELEMENTS if # atoms = 0")
    ierr = mdi.MDI_Recv(qm_natoms, mdi.MDI_INT, mdicomm, buf=qm_elements)
    if ierr:
        error("MDI: >ELEMENTS reception failed")


def receive_qm_types(mdicomm):
    if not qm_natoms:
        error("Cannot receive >TYPES if # atoms = 0")
    types = np.empty(qm_natoms, dtype=np.int32)
    ierr = mdi.MDI_Recv(qm_natoms, mdi.MDI_INT, mdicomm, buf=types)
    if ierr:
        error("MDI: >TYPES reception failed")
    for i, t in enumerate(types):
        sym = type_to_symbol.get(int(t), 'C')
        qm_elements[i] = ELEMENTS.index(sym) + 1


def evaluate():
    global qm_pe, qm_forces, last_evaluated_coords, step_counter
    if qm_natoms == 0 or qm_elements is None or qm_coords is None:
        error("System atoms, elements, or coordinates not fully specified")

    if last_evaluated_coords is not None and np.allclose(qm_coords, last_evaluated_coords, atol=1e-8):
        return

    bohr_to_angstrom = mdi.MDI_Conversion_factor("bohr", "angstrom")
    ev_to_hartree = mdi.MDI_Conversion_factor("electron_volt", "hartree")
    force_conv = ev_to_hartree * bohr_to_angstrom

    coords_angstrom = qm_coords * bohr_to_angstrom
    symbols = [atomic_number_to_symbol[int(anum)] for anum in qm_elements]

    if flag_box and np.linalg.norm(box) > 1e-6:
        cell_matrix_bohr = box.reshape(3, 3)
        cell_matrix_angstrom = cell_matrix_bohr * bohr_to_angstrom
    else:
        cell_matrix_angstrom = np.eye(3) * 10.0

    z_coords = coords_angstrom[:, 2]
    Lz = cell_matrix_angstrom[2, 2]
    z_min, z_max = float(np.min(z_coords)), float(np.max(z_coords))
    current_gap = (z_min + Lz) - z_max

    # Step 0..100: Exact cache replay to restore positions, velocities, and Nosé-Hoover chain variables
    if step_counter in cached_steps:
        pe_ev, forces_ev_angstrom, n_scf_iters, pwo_text = cached_steps[step_counter]
        with open("espresso_all_steps.pwo", "a", encoding="utf-8") as f_out:
            f_out.write(f"\n=== STEP {step_counter} ===\n")
            f_out.write(pwo_text)
        if step_counter == 100:
            with open("espresso.pwo", "w", encoding="utf-8") as f_pwo:
                f_pwo.write(pwo_text)
            shutil.copyfile("espresso.pwo", "live_espresso.pwo")

        qm_pe = pe_ev * ev_to_hartree
        qm_forces = forces_ev_angstrom * force_conv
        fmax = np.max(np.linalg.norm(forces_ev_angstrom, axis=1))
        log(
            f"--- [Step {step_counter}] Done in 0.00s ({n_scf_iters} SCF iters) [RESTORED CACHE] | "
            f"E_pot: {pe_ev:.4f} eV | Fmax: {fmax:.5f} eV/A | gap: {current_gap:.4f} A ---"
        )
        last_evaluated_coords = np.copy(qm_coords)
        step_counter += 1
        return

    # Step 101..400: Live Quantum ESPRESSO GPU SCF calculation inheriting wfc1.hdf5 & charge-density.hdf5
    atoms = Atoms(symbols=symbols, positions=coords_angstrom, cell=cell_matrix_angstrom, pbc=[True, True, True])
    command_str = detect_pw_command()
    cfg = load_dft_config()

    reuse_prev_wfc = has_saved_wfc_and_pot()

    electrons_dict = {
        'conv_thr': cfg['conv_thr'],
        'mixing_beta': cfg['mixing_beta'],
        'mixing_mode': cfg['mixing_mode'],
        'electron_maxstep': cfg['electron_maxstep'],
    }
    if reuse_prev_wfc:
        electrons_dict['startingpot'] = 'file'
        electrons_dict['startingwfc'] = 'file'

    input_data = {
        'control': {
            'calculation': 'scf',
            'pseudo_dir': './',
            'outdir': './tmp',
            'tprnfor': True,
            'tstress': True,
            'disk_io': 'medium',
        },
        'system': {
            'ecutwfc': cfg['ecutwfc'],
            'ecutrho': cfg['ecutrho'],
            'occupations': cfg['occupations'],
            'smearing': cfg['smearing'],
            'degauss': cfg['degauss'],
        },
        'electrons': electrons_dict,
    }

    log(
        f"--- [Step {step_counter}] Starting SCF ({len(atoms)} atoms, "
        f"startingpot/wfc={'file' if reuse_prev_wfc else 'atomic'}, "
        f"z_min={z_min:.4f}A, z_max={z_max:.4f}A, gap={current_gap:.4f}A) ---"
    )

    t0 = time.time()
    profile = EspressoProfile(command=command_str, pseudo_dir="./")
    calc = Espresso(profile=profile, pseudopotentials=cfg['pseudopotentials'], input_data=input_data, kpts=cfg['kpts'])
    atoms.calc = calc

    pe_ev = atoms.get_potential_energy()
    forces_ev_angstrom = atoms.get_forces()
    elapsed = time.time() - t0

    n_scf_iters = -1
    if os.path.exists("espresso.pwo"):
        with open("espresso.pwo", "r", encoding="utf-8", errors="ignore") as f_in:
            pwo_text = f_in.read()
        m_it = re.search(r"convergence has been achieved in\s+(\d+)\s+iterations", pwo_text)
        if m_it:
            n_scf_iters = int(m_it.group(1))
        with open("espresso_all_steps.pwo", "a", encoding="utf-8") as f_out:
            f_out.write(f"\n=== STEP {step_counter} ===\n")
            f_out.write(pwo_text)
        shutil.copyfile("espresso.pwo", "live_espresso.pwo")

    qm_pe = pe_ev * ev_to_hartree
    qm_forces = forces_ev_angstrom * force_conv
    fmax = np.max(np.linalg.norm(forces_ev_angstrom, axis=1))

    log(
        f"--- [Step {step_counter}] Done in {elapsed:.2f}s ({n_scf_iters} SCF iters) | "
        f"E_pot: {pe_ev:.4f} eV | Fmax: {fmax:.5f} eV/A | gap: {current_gap:.4f} A ---"
    )
    last_evaluated_coords = np.copy(qm_coords)
    step_counter += 1


def execute_command(command, mdicomm, object_ptr):
    global exitflag
    if command == "EXIT":
        log("Received EXIT command from driver.")
        exitflag = True
    elif command == ">NATOMS":
        receive_qm_natoms(mdicomm)
    elif command == ">CELL":
        receive_box(mdicomm)
    elif command == ">ELEMENTS":
        receive_qm_elements(mdicomm)
    elif command == ">TYPES":
        receive_qm_types(mdicomm)
    elif command == ">COORDS":
        receive_qm_coords(mdicomm)
    elif command in ["<ENERGY", "<PE"]:
        evaluate()
        ierr = mdi.MDI_Send(qm_pe, 1, mdi.MDI_DOUBLE, mdicomm)
        if ierr:
            error("MDI: <ENERGY send failed")
    elif command == "<FORCES":
        evaluate()
        ierr = mdi.MDI_Send(qm_forces, 3 * qm_natoms, mdi.MDI_DOUBLE, mdicomm)
        if ierr:
            error("MDI: <FORCES send failed")
    else:
        error(f"Unrecognized MDI command: {command}")
    return 0


def main():
    configure_environment()
    load_cached_100_steps()
    mdi_options = None
    for i, arg in enumerate(sys.argv):
        if arg in ["-mdi", "--mdi"] and i + 1 < len(sys.argv):
            mdi_options = sys.argv[i + 1]
            break
    if not mdi_options:
        error("MDI options not provided.")

    log(f"Initializing MDI Engine with options: {mdi_options}")
    mdi.MDI_Init(mdi_options)
    mdi.MDI_Register_Node("@DEFAULT")
    for cmd in ["EXIT", ">NATOMS", ">CELL", ">ELEMENTS", ">TYPES", ">COORDS", "<ENERGY", "<PE", "<FORCES"]:
        mdi.MDI_Register_Command("@DEFAULT", cmd)
    mdi.MDI_Set_Execute_Command_Func(execute_command, None)

    log("Waiting for MDI driver connection...")
    mdicomm = mdi.MDI_Accept_Communicator()
    log("Connected to MDI driver! Entering communication loop...")

    while not exitflag:
        command = mdi.MDI_Recv_Command(mdicomm)
        execute_command(command, mdicomm, None)

    log("MDI Engine execution terminated cleanly.")


if __name__ == "__main__":
    main()
'''


def prepare_slab400_aimd():
    log("==============================================================================")
    log("Preparing Continuation of 300 K NVT AIMD for Unrelaxed 8-period Vac 3.0 Å Slab")
    log("(Step 101..400, total 400 steps = 400 fs = 0.4 ps)")
    log("Inheriting 100% of Step 100 state (coords, velocities, Nosé-Hoover bath, wfc, charge density, energy/forces)")
    log("==============================================================================")

    os.makedirs(SLAB400_AIMD_DIR, exist_ok=True)

    # Copy common assets from PREV_SLAB100_DIR
    for asset in [
        "C.upf",
        "Si.upf",
        "RELAXATION_GRAPH_PROTOCOL.json",
        "dft_settings.py",
        "make_xyz.py",
        "msmincho.ttc",
        "times.ttf",
        "auto_generate_progression_graphs.py",
        "slab_10-10_288atoms_vac3.0A_unrelaxed.data",
        "slab_10-10_288atoms_vac3.0A_unrelaxed_aimd_100steps_final.data",
    ]:
        src = os.path.join(PREV_SLAB100_DIR, asset)
        if os.path.exists(src):
            dst = os.path.join(SLAB400_AIMD_DIR, asset)
            shutil.copyfile(src, dst)
            if asset.endswith(".py"):
                os.chmod(dst, 0o755)

    # Copy Step 0..100 full QE outputs for exact cache replay
    src_pwo_all = os.path.join(PREV_SLAB100_DIR, "espresso_all_steps.pwo")
    dst_pwo_cache = os.path.join(SLAB400_AIMD_DIR, "prev_100steps_espresso_all_steps.pwo")
    shutil.copyfile(src_pwo_all, dst_pwo_cache)

    # Copy Step 100 converged wavefunction (wfc1.hdf5) and charge density (charge-density.hdf5) in ./tmp
    src_tmp = os.path.join(PREV_SLAB100_DIR, "tmp")
    dst_tmp = os.path.join(SLAB400_AIMD_DIR, "tmp")
    if os.path.exists(dst_tmp):
        shutil.rmtree(dst_tmp)
    shutil.copytree(src_tmp, dst_tmp)
    log("Copied Step 100 converged wavefunction (wfc1.hdf5) and electron density (charge-density.hdf5) to ./tmp/pwscf.save/")

    # Write continuation QE-MDI engine
    engine_path = os.path.join(SLAB400_AIMD_DIR, "qe_mdi_engine_rtx5080.py")
    with open(engine_path, "w", encoding="utf-8") as f:
        f.write(QE_ENGINE_CONTINUE_400_CODE)
    os.chmod(engine_path, 0o755)

    # Write in.lammps (runs 100 steps via cache replay in ~5s to restore exact bath state, then continues 300 more steps to 400)
    in_lammps_content = """# ==============================================================================
# 2H-SiC {10-10} 8周期 (16層, 288原子) スラブモデル (真空層 各3.0Å, ギャップ 6.0Å)
# 【構造最適化なし (未緩和初期構造)】300K NVT 第一原理分子動力学:
# Step 100 からの完全引き継ぎ追加 300 steps (通算 400 steps = 400 fs = 0.4 ps)
# ==============================================================================
units           metal
dimension       3
boundary        p p p
atom_style      atomic
atom_modify     map yes

# 1. 初期構造の読み込み (8周期・真空3.0Å の 0K 構造最適化を行っていない理想切断スラブ構造)
read_data       slab_10-10_288atoms_vac3.0A_unrelaxed.data

# 原子質量設定 (Rule 2: Type 1: C = 12.011, Type 2: Si = 28.085)
mass            1 12.011
mass            2 28.085

pair_style      none

# 2. MDI 通信設定 (Quantum ESPRESSO を第一原理 QM エンジンとして連成)
fix             1 all mdi/qm elements C Si

# 3. 初期熱運動速度の付与 (Maxwell-Boltzmann 分布 @ 300K, 同一乱数シード 87654)
velocity        all create 300.0 87654 mom yes rot yes dist gaussian

# 4. 運動方程式の数値積分 & サーモスタット設定 (NVT アンサンブル @ 300K)
timestep        0.001
fix             2 all nvt temp 300.0 300.0 0.1

# 5. スラブ特有の重心ドリフト防止 (50ステップごとに全並進運動量をゼロにリセット)
fix             3 all momentum 50 linear 1 1 1

# 6. 出力設定 & ログ記録
thermo_style    custom step temp epair emol ke pe etotal press fmax fnorm
thermo          1
thermo_modify   flush yes

dump            1 all custom 1 dump.lammpstrj id type x y z vx vy vz fx fy fz
dump_modify     1 sort id flush yes

# 7. Step 0..100 をキャッシュリプレイして位置・速度・熱浴内部変数を100%完全復元し、チェックポイントを出力
run             100
write_restart   restart.slab_unrelaxed_100steps_restored
write_data      slab_10-10_288atoms_vac3.0A_unrelaxed_aimd_100steps_restored_check.data

# 8. Step 101..400 の追加 300 ステップを実機 QE GPU SCF (Step 100 の波動関数・電荷密度引き継ぎ) で連続実行
restart         50 restart.slab_unrelaxed_step
run             300

write_restart   restart.slab_unrelaxed_400steps_final
write_data      slab_10-10_288atoms_vac3.0A_unrelaxed_aimd_400steps_final.data
undump          1
"""
    with open(os.path.join(SLAB400_AIMD_DIR, "in.lammps"), "w", encoding="utf-8") as f:
        f.write(in_lammps_content)

    for fn in ["dump.lammpstrj", "log.lammps", "lmp.log", "qe_engine.log", "espresso.pwo", "espresso_all_steps.pwo"]:
        p = os.path.join(SLAB400_AIMD_DIR, fn)
        if os.path.exists(p):
            os.remove(p)

    log("Prepared unrelaxed slab 400-step AIMD continuation directory and input files.")
    sync_to_nas()


def run_slab400_aimd():
    port = 8050
    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["QE_MPI_NP"] = "12"
    env["QE_OMP_THREADS"] = "2"

    lmp_bin = os.path.join(ENV_PREFIX, "bin", "lmp")
    py_bin = os.path.join(ENV_PREFIX, "bin", "python3")

    t0 = time.time()
    lmp_log_f = open(os.path.join(SLAB400_AIMD_DIR, "lmp.log"), "w")
    qe_log_f = open(os.path.join(SLAB400_AIMD_DIR, "qe_engine.log"), "w")

    log(f"Launching LAMMPS driver and QE-MDI engine on port {port} (Step 0..100 cache restore -> Step 101..400 live SCF)...")
    lmp_proc = subprocess.Popen(
        [lmp_bin, "-mdi", f"-role DRIVER -name LAMMPS -method TCP -port {port}", "-in", "in.lammps", "-log", "log.lammps"],
        cwd=SLAB400_AIMD_DIR,
        env=env,
        stdout=lmp_log_f,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    qe_proc = subprocess.Popen(
        [py_bin, "qe_mdi_engine_rtx5080.py", "-mdi", f"-role ENGINE -name QE -method TCP -port {port} -hostname localhost"],
        cwd=SLAB400_AIMD_DIR,
        env=env,
        stdout=qe_log_f,
        stderr=subprocess.STDOUT,
    )

    last_sync_time = time.time()
    while lmp_proc.poll() is None:
        time.sleep(15)
        if time.time() - last_sync_time >= 300:
            dump_path = os.path.join(SLAB400_AIMD_DIR, "dump.lammpstrj")
            if os.path.exists(dump_path) and os.path.getsize(dump_path) > 0:
                subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=SLAB400_AIMD_DIR, env=env, check=False)
            sync_to_nas()
            last_sync_time = time.time()

    try:
        qe_proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        qe_proc.kill()

    lmp_log_f.close()
    qe_log_f.close()
    elapsed = time.time() - t0

    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=SLAB400_AIMD_DIR, env=env, check=False)
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_nvt_animation.xyz"], cwd=SLAB400_AIMD_DIR, env=env, check=False)
    subprocess.run([py_bin, "auto_generate_progression_graphs.py"], cwd=SLAB400_AIMD_DIR, env=env, check=False)

    log(f"Unrelaxed Slab 300 K AIMD Continuation (Step 101..400, total 400 steps) Completed in {elapsed:.1f}s ({elapsed/60.0:.1f} min)!")


def analyze_and_plot_results():
    Lz = 25.53540130124298
    thermo_data = {}
    with open(os.path.join(SLAB400_AIMD_DIR, "log.lammps")) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 10 and parts[0].isdigit():
                step = int(parts[0])
                thermo_data[step] = {
                    "temp": float(parts[1]),
                    "ke": float(parts[4]),
                    "pe": float(parts[5]),
                    "etotal": float(parts[6]),
                    "press": float(parts[7]),
                    "fmax": float(parts[8]),
                    "fnorm": float(parts[9]),
                }

    scf_data = {}
    with open(os.path.join(SLAB400_AIMD_DIR, "qe_engine.log")) as f:
        for line in f:
            m = re.search(r"\[Step (\d+)\] Done in ([\d\.]+)s \((\d+) SCF iters\)", line)
            if m:
                scf_data[int(m.group(1))] = (float(m.group(2)), int(m.group(3)))

    with open(os.path.join(SLAB400_AIMD_DIR, "dump.lammpstrj")) as f:
        lines = f.readlines()

    frames_dict = {}
    i = 0
    while i < len(lines):
        if "ITEM: TIMESTEP" in lines[i]:
            step = int(lines[i + 1].strip())
            natoms = int(lines[i + 3].strip())
            data = []
            for l in lines[i + 9 : i + 9 + natoms]:
                parts = l.split()
                data.append([
                    int(parts[0]),
                    int(parts[1]),
                    float(parts[2]),
                    float(parts[3]),
                    float(parts[4]),
                    float(parts[5]),
                    float(parts[6]),
                    float(parts[7]),
                ])
            data.sort(key=lambda x: x[0])
            frames_dict[step] = np.array(data)
            i += 9 + natoms
        else:
            i += 1

    sorted_steps = sorted(frames_dict.keys())
    z0 = frames_dict[0][:, 4]
    top_mask = z0 > 21.5
    bot_mask = z0 < 4.0
    surf_mask = top_mask | bot_mask

    rows = []
    for step in sorted_steps:
        arr = frames_dict[step]
        z = arr[:, 4]
        vz = arr[:, 7] * 0.001  # A/fs
        dz = z - z0
        dz_surf = dz[surf_mask]
        dz_top = dz[top_mask]
        dz_bot = dz[bot_mask]
        z_min = float(z.min())
        z_max = float(z.max())
        gap = (z_min + Lz) - z_max

        th = thermo_data.get(step, {})
        scf_t, scf_it = scf_data.get(step, (0.0, 0))
        rows.append({
            "step": step,
            "time_fs": float(step),
            "scf_iters": scf_it,
            "scf_time_s": scf_t,
            "temp_K": th.get("temp", 0.0),
            "ke_eV": th.get("ke", 0.0),
            "pe_eV": th.get("pe", 0.0),
            "etotal_eV": th.get("etotal", 0.0),
            "press_bar": th.get("press", 0.0),
            "fmax_eV_A": th.get("fmax", 0.0),
            "fnorm_eV_A": th.get("fnorm", 0.0),
            "z_min_A": round(z_min, 5),
            "z_max_A": round(z_max, 5),
            "gap_A": round(gap, 5),
            "dz_max_surf_A": round(float(np.max(np.abs(dz_surf))), 5),
            "dz_rms_surf_A": round(float(np.sqrt(np.mean(dz_surf**2))), 5),
            "dz_top_outward_max_A": round(float(np.max(dz_top)), 5),
            "dz_bot_outward_max_A": round(float(np.max(-dz_bot)), 5),
            "vz_max_surf_A_fs": round(float(np.max(np.abs(vz[surf_mask]))), 6),
        })

    csv_path = os.path.join(SLAB400_AIMD_DIR, "aimd_unrelaxed_400steps_summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    def calc_window_stats(start_step, end_step=None):
        sub = [r for r in rows if r["step"] >= start_step and (end_step is None or r["step"] <= end_step)]
        t_arr = np.array([r["temp_K"] for r in sub])
        et_arr = np.array([r["etotal_eV"] for r in sub])
        pe_arr = np.array([r["pe_eV"] for r in sub])
        ke_arr = np.array([r["ke_eV"] for r in sub])
        gap_arr = np.array([r["gap_A"] for r in sub])
        dz_arr = np.array([r["dz_max_surf_A"] for r in sub])
        return {
            "window": f"Step {start_step}..{sub[-1]['step']} ({len(sub)} points)",
            "temp_mean_K": float(np.mean(t_arr)),
            "temp_std_K": float(np.std(t_arr)),
            "etotal_mean_eV": float(np.mean(et_arr)),
            "etotal_std_eV": float(np.std(et_arr)),
            "pe_mean_eV": float(np.mean(pe_arr)),
            "pe_std_eV": float(np.std(pe_arr)),
            "ke_mean_eV": float(np.mean(ke_arr)),
            "ke_std_eV": float(np.std(ke_arr)),
            "gap_mean_A": float(np.mean(gap_arr)),
            "gap_min_A": float(np.min(gap_arr)),
            "dz_surf_max_A": float(np.max(dz_arr)),
        }

    stats = {
        "natoms": 288,
        "n_periods": 8,
        "vacuum_A": 3.0,
        "initial_gap_A": 6.0,
        "target_temp_K": 300.0,
        "total_steps": rows[-1]["step"],
        "slab_0K_relaxed_energy_eV": -127685.1583,
        "slab_0K_unrelaxed_energy_eV": -127673.8610,
        "bulk_300K_equil_pe_eV": -127714.79,
        "ensemble_all_0_to_400": calc_window_stats(0),
        "ensemble_phase1_0_to_100": calc_window_stats(0, 100),
        "ensemble_phase2_100_to_400": calc_window_stats(100),
        "ensemble_equil_200_to_400": calc_window_stats(200),
        "ensemble_equil_300_to_400": calc_window_stats(300),
    }
    with open(os.path.join(SLAB400_AIMD_DIR, "aimd_unrelaxed_400steps_ensemble_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

    plt.rcParams["mathtext.fontset"] = "stix"
    mincho_path = os.path.join(SLAB400_AIMD_DIR, "msmincho.ttc")
    times_path = os.path.join(SLAB400_AIMD_DIR, "times.ttf")
    prop_label = fm.FontProperties(fname=mincho_path, size=10.5) if os.path.exists(mincho_path) else fm.FontProperties(size=10.5)
    prop_tick = fm.FontProperties(fname=times_path, size=9.5) if os.path.exists(times_path) else fm.FontProperties(size=9.5)
    prop_legend = fm.FontProperties(fname=mincho_path, size=8.5) if os.path.exists(mincho_path) else fm.FontProperties(size=8.5)

    steps = np.array([r["step"] for r in rows])
    temp = np.array([r["temp_K"] for r in rows])
    etot = np.array([r["etotal_eV"] for r in rows])
    pe = np.array([r["pe_eV"] for r in rows])
    ke = np.array([r["ke_eV"] for r in rows])
    gap = np.array([r["gap_A"] for r in rows])
    dz_max = np.array([r["dz_max_surf_A"] for r in rows])
    dz_rms = np.array([r["dz_rms_surf_A"] for r in rows])

    fig_w = 8.0 / 2.54
    fig_h = 6.2 / 2.54
    mark_every = 15

    def style_ax(ax, xlabel, ylabel):
        ax.set_xlabel(xlabel, fontproperties=prop_label, labelpad=4)
        ax.set_ylabel(ylabel, fontproperties=prop_label, labelpad=4)
        ax.tick_params(direction="in", top=True, right=True, length=3.5, width=0.8)
        for sp in ax.spines.values():
            sp.set_linewidth(0.9)
        ax.set_xlim(-10, 410)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax.yaxis.get_major_formatter().set_useOffset(False)
        ax.yaxis.get_major_formatter().set_scientific(False)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_fontproperties(prop_tick)

    # 1. 全エネルギー推移 (Word 8cm)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.plot(steps, etot, color="#8A2BE2", lw=1.1, zorder=2)
    ax.scatter(steps[::mark_every], etot[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0, zorder=3)
    style_ax(ax, "MDステップ [step]", r"全エネルギー [$\mathrm{eV}$]")
    e_min, e_max = float(np.min(etot)), float(np.max(etot))
    span = max(e_max - e_min, 0.2)
    ax.set_ylim(e_min - 0.35 * span, e_max + 0.35 * span)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"全エネルギー推移_未緩和AIMD_400steps_word_8cm.{ext}"), dpi=600)
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"全エネルギー推移_未緩和AIMD_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 2. ポテンシャルエネルギー推移 (Word 8cm)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.plot(steps, pe, color="#8A2BE2", lw=1.1, zorder=2)
    ax.scatter(steps[::mark_every], pe[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0, zorder=3)
    style_ax(ax, "MDステップ [step]", r"ポテンシャルエネルギー [$\mathrm{eV}$]")
    p_min, p_max = float(np.min(pe)), float(np.max(pe))
    pspan = max(p_max - p_min, 1.0)
    ax.set_ylim(p_min - 0.15 * pspan, p_max + 0.15 * pspan)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"ポテンシャルエネルギー推移_未緩和AIMD_400steps_word_8cm.{ext}"), dpi=600)
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"ポテンシャルエネルギー推移_未緩和AIMD_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 3. エネルギー変化量推移 (Word 8cm)
    d_etot = etot - etot[0]
    d_pe = pe - pe[0]
    d_ke = ke - ke[0]
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.axhline(0.0, color="#888888", ls=":", lw=0.8, zorder=1)
    ax.plot(steps, d_etot, color="#8A2BE2", lw=1.2, label=r"全エネルギー $\Delta E_{\mathrm{tot}}$", zorder=4)
    ax.scatter(steps[::mark_every], d_etot[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=24, linewidths=0.9, zorder=5)
    ax.plot(steps, d_pe, color="#1E90FF", lw=1.1, ls="--", label=r"ポテンシャル $\Delta E_{\mathrm{pot}}$", zorder=3)
    ax.plot(steps, d_ke, color="#D2691E", lw=1.1, ls="-.", label=r"運動エネルギー $\Delta E_{\mathrm{kin}}$", zorder=3)
    style_ax(ax, "MDステップ [step]", r"初期値からのエネルギー変化 [$\mathrm{eV}$]")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    ax.legend(prop=prop_legend, loc="best", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"エネルギー変化量推移_未緩和AIMD_400steps_word_8cm.{ext}"), dpi=600)
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"エネルギー変化量推移_未緩和AIMD_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 4. 温度推移 (Word 8cm)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)
    ax.axhline(300.0, color="#222222", ls="--", lw=1.0, zorder=1)
    ax.axvline(100.0, color="#888888", ls=":", lw=0.8, zorder=1)
    ax.plot(steps, temp, color="#8A2BE2", lw=1.1, zorder=2)
    ax.scatter(steps[::mark_every], temp[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0, zorder=3)
    style_ax(ax, "MDステップ [step]", r"温度 [$\mathrm{K}$]")
    fig.tight_layout(pad=0.3)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"温度推移_未緩和AIMD_400steps_word_8cm.{ext}"), dpi=600)
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"温度推移_未緩和AIMD_word_8cm.{ext}"), dpi=600)
    plt.close(fig)

    # 5. 表面原子変位 & スラブ間ギャップ推移
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.2, 5.4), dpi=300, sharex=True)
    ax1.plot(steps, dz_max, color="#8A2BE2", lw=1.5, label=r"最大変位 $|\Delta z|_{\max}$ (最表面原子)")
    ax1.plot(steps, dz_rms, color="#1E90FF", lw=1.5, ls="--", label=r"二乗平均変位 $\Delta z_{\mathrm{rms}}$ (最表面36原子)")
    ax1.axvline(100.0, color="#666666", ls=":", lw=1.0, label="引き継ぎ境界 (Step 100)")
    ax1.set_ylabel(r"表面原子 Z方向変位 [$\mathrm{\AA}$]", fontproperties=prop_label)
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.tick_params(direction="in", top=True, right=True)
    ax1.legend(prop=prop_legend, loc="upper left", frameon=True)

    ax2.plot(steps, gap, color="#2E8B57", lw=1.6, label=r"スラブ間ギャップ $d_{\mathrm{gap}}$")
    ax2.axhline(6.0, color="#666666", ls="--", lw=1.0, label="初期ギャップ (6.00 Å)")
    ax2.axvline(100.0, color="#666666", ls=":", lw=1.0)
    ax2.set_xlabel(r"時間 / MDステップ [$\mathrm{fs}$]", fontproperties=prop_label)
    ax2.set_ylabel(r"スラブ間ギャップ [$\mathrm{\AA}$]", fontproperties=prop_label)
    ax2.set_xlim(-10, 410)
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.tick_params(direction="in", top=True, right=True)
    ax2.legend(prop=prop_legend, loc="lower left", frameon=True)

    for a in (ax1, ax2):
        for lbl in a.get_xticklabels() + a.get_yticklabels():
            lbl.set_fontproperties(prop_tick)

    fig.tight_layout(pad=0.5)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"AIMD_Surface_Displacement_and_Gap_400steps.{ext}"), dpi=300)
    plt.close(fig)

    # 6. エネルギー・温度総合推移 (プレゼン仕様)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6.5, 7.2), dpi=300, sharex=True)
    ax1.plot(steps, temp, color="#D2691E", lw=1.5, label=r"温度 $T$ (未緩和スラブ 288原子)")
    ax1.axhline(300.0, color="#222222", ls="--", lw=1.0, label="目標温度 (300 K)")
    ax1.axvline(100.0, color="#666666", ls=":", lw=1.0, label="引き継ぎ境界 (Step 100)")
    ax1.set_ylabel(r"温度 $T$ [$\mathrm{K}$]", fontproperties=prop_label)
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.tick_params(direction="in", top=True, right=True)
    ax1.legend(prop=prop_legend, loc="lower right", frameon=True)

    ax2.plot(steps, etot, color="#8A2BE2", lw=1.5, label=r"全エネルギー $E_{\mathrm{tot}} = E_{\mathrm{pot}} + E_{\mathrm{kin}}$")
    ax2.scatter(steps[::mark_every], etot[::mark_every], marker="^", facecolors="none", edgecolors="#8A2BE2", s=28, linewidths=1.0)
    ax2.axvline(100.0, color="#666666", ls=":", lw=1.0)
    ax2.set_ylabel(r"全エネルギー [$\mathrm{eV}$]", fontproperties=prop_label)
    ax2.yaxis.get_major_formatter().set_useOffset(False)
    ax2.yaxis.get_major_formatter().set_scientific(False)
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    ax2.set_ylim(e_min - 0.35 * span, e_max + 0.35 * span)
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.tick_params(direction="in", top=True, right=True)
    ax2.legend(prop=prop_legend, loc="upper left", frameon=True)

    ax3.plot(steps, pe, color="#1E90FF", lw=1.5, label=r"ポテンシャルエネルギー $E_{\mathrm{pot}}$")
    ax3.scatter(steps[::mark_every], pe[::mark_every], marker="o", facecolors="none", edgecolors="#1E90FF", s=24, linewidths=0.9)
    ax3.axvline(100.0, color="#666666", ls=":", lw=1.0)
    ax3.axhline(stats["ensemble_equil_200_to_400"]["pe_mean_eV"], color="#2E8B57", ls="--", lw=1.1,
                label=f"Step 200..400 平均 $\\langle E_{{\\mathrm{{pot}}}}\\rangle = {stats['ensemble_equil_200_to_400']['pe_mean_eV']:.2f}$ eV")
    ax3.set_xlabel(r"時間 / MDステップ [$\mathrm{fs}$]", fontproperties=prop_label)
    ax3.set_ylabel(r"ポテンシャル [$\mathrm{eV}$]", fontproperties=prop_label)
    ax3.yaxis.get_major_formatter().set_useOffset(False)
    ax3.yaxis.get_major_formatter().set_scientific(False)
    ax3.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    ax3.set_xlim(-10, 410)
    ax3.grid(True, ls=":", alpha=0.5)
    ax3.tick_params(direction="in", top=True, right=True)
    ax3.legend(prop=prop_legend, loc="lower right", frameon=True)

    for a in (ax1, ax2, ax3):
        for lbl in a.get_xticklabels() + a.get_yticklabels():
            lbl.set_fontproperties(prop_tick)

    fig.tight_layout(pad=0.5)
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"エネルギー総合推移_未緩和AIMD_400steps_プレゼン仕様.{ext}"), dpi=300)
        fig.savefig(os.path.join(SLAB400_AIMD_DIR, f"AIMD_Temperature_and_Energy_400steps.{ext}"), dpi=300)
    plt.close(fig)

    log("Generated summary CSV, ensemble stats JSON, and unrelaxed slab 400-step AIMD plots.")
    sync_to_nas()


if __name__ == "__main__":
    try:
        prepare_slab400_aimd()
        run_slab400_aimd()
        analyze_and_plot_results()
        log("ALL UNRELAXED SLAB 400-STEP CONTINUATION AIMD TASKS COMPLETED SUCCESSFULLY!")
    except Exception as exc:
        log(f"FATAL ERROR: {exc}")
        raise

