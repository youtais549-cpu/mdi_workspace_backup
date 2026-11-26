#!/usr/bin/env python3
"""
==============================================================================
Quantum ESPRESSO + MDI 連成エンジン (RTX 5080 16GB + Core Ultra 9 285K 24コア最適化版)
==============================================================================
・2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 5.0 Å スラブ構造緩和用
・Core Ultra 9 285K (24コア / 64GB RAM) + RTX 5080 (16GB VRAM) 環境向け
・ASE + MDI DummyMPI 適用 (AGENTS.md §3)
・Type 1 = C (12.011), Type 2 = Si (28.085) 厳格一致 (AGENTS.md §2)
"""
import sys
import os
import glob
import shutil
import subprocess
import time
import numpy as np
import mdi
from ase import Atoms
from ase.calculators.espresso import Espresso, EspressoProfile
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
# Rule 2: Type 1 = C (12.011), Type 2 = Si (28.085)
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


def log(msg):
    print(f"[QE-MDI RTX5080 Engine] {msg}", flush=True)


def error(txt):
    log(f"ERROR: {txt}")
    sys.exit(1)


def configure_rtx5080_environment():
    """
    RTX 5080 (Blackwell sm_120, 16GB VRAM) & Core Ultra 9 285K (24コア) 用環境変数の設定
    """
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
        log(f"Detected NVHPC SDK at: {root}")

    cuda_libs = [
        "/usr/local/cuda/lib64",
        "/usr/lib/wsl/lib",
        "/usr/lib/x86_64-linux-gnu",
    ]
    existing_libs = [p for p in (extra_libs + cuda_libs) if os.path.exists(p)]
    current_ld = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = ":".join(existing_libs + ([current_ld] if current_ld else []))


def query_rtx5080_status():
    """nvidia-smi から RTX 5080 の現在の VRAM 使用量・温度・消費電力を取得"""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=3,
        ).strip()
        if out:
            parts = [p.strip() for p in out.split(",")]
            if len(parts) >= 6:
                return (
                    f"GPU: {parts[0]} | VRAM: {parts[1]}/{parts[2]} MiB | "
                    f"Util: {parts[3]}% | Temp: {parts[4]}C | Power: {parts[5]}W"
                )
    except Exception:
        pass
    return "GPU status unavailable"


def detect_pw_command():
    """
    ローカル環境 (WSL2 Ubuntu) の pw.x バイナリを検出し、
    GPU ビルドか CPU/MPI ビルドかを自動判定して最適な起動コマンドを返す。
    """
    env_pw = os.environ.get("QE_PW_COMMAND")
    if env_pw:
        log(f"Using user-specified QE_PW_COMMAND: {env_pw}")
        return env_pw

    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    home_dir = os.path.expanduser("~")

    candidates = [
        os.path.join(script_dir, "bin", "pw.x"),
        "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080/bin/pw.x",
        os.path.join(workspace_dir, "calc_2H-SiC_10-10_2periods_vac5A_local_RTX5080", "bin", "pw.x"),
        os.path.join(workspace_dir, "bin", "pw.x"),
        os.path.join(home_dir, ".local", "bin", "pw.x"),
        "/usr/local/bin/pw.x",
        shutil.which("pw.x"),
    ]
    pw_bin = None
    for cand in candidates:
        if cand and os.path.exists(cand) and os.access(cand, os.X_OK):
            pw_bin = cand
            break

    if not pw_bin:
        error("pw.x binary not found!")

    is_gpu_binary = False
    try:
        ldd_out = subprocess.check_output(["ldd", pw_bin], text=True, stderr=subprocess.DEVNULL)
        if any(k in ldd_out for k in ["libcuda", "libcudart", "libacc", "libnvf", "libcufft", "libcublas"]):
            is_gpu_binary = True
    except Exception:
        pass

    if is_gpu_binary:
        os.environ.setdefault("OMP_NUM_THREADS", os.environ.get("QE_OMP_THREADS", "8"))
        cmd = f"{pw_bin} -ndiag 1"
        log(f"Detected GPU-accelerated pw.x: {cmd} (OMP_NUM_THREADS={os.environ['OMP_NUM_THREADS']})")
        return cmd
    else:
        # Core Ultra 9 285K (24コア) を最大限活用: 12 MPI × 2 OpenMP = 24 threads
        mpi_np = int(os.environ.get("QE_MPI_NP", "12"))
        omp_threads = os.environ.get("QE_OMP_THREADS", "2")
        os.environ["OMP_NUM_THREADS"] = omp_threads
        mpirun_bin = shutil.which("mpirun") or "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080/bin/mpirun"
        if mpirun_bin and os.path.exists(mpirun_bin) and mpi_np > 1:
            cmd = f"{mpirun_bin} --oversubscribe -np {mpi_np} {pw_bin} -ndiag 1"
        else:
            cmd = f"{pw_bin} -ndiag 1"
        log(f"Detected CPU/MPI pw.x: {cmd} (MPI_NP={mpi_np}, OMP_NUM_THREADS={omp_threads})")
        return cmd


def load_dft_config():
    """外部の dft_settings.py から DFT 条件を動的に読み込み"""
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
                log("Loaded DFT_CONFIG from dft_settings.py")
    except Exception as e:
        log(f"Notice: Using default DFT parameters ({e})")
    return default_config


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

    # 座標キャッシュ: 同一ステップでの重複 SCF 計算を防止
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

    atoms = Atoms(symbols=symbols, positions=coords_angstrom, cell=cell_matrix_angstrom, pbc=[True, True, True])
    command_str = detect_pw_command()
    cfg = load_dft_config()

    input_data = {
        'control': {
            'calculation': 'scf',
            'pseudo_dir': './',
            'outdir': './tmp',
            'tprnfor': True,
            'tstress': True,
            'disk_io': 'minimal',
        },
        'system': {
            'ecutwfc': cfg['ecutwfc'],
            'ecutrho': cfg['ecutrho'],
            'occupations': cfg['occupations'],
            'smearing': cfg['smearing'],
            'degauss': cfg['degauss'],
        },
        'electrons': {
            'conv_thr': cfg['conv_thr'],
            'mixing_beta': cfg['mixing_beta'],
            'mixing_mode': cfg['mixing_mode'],
            'electron_maxstep': cfg['electron_maxstep'],
        },
    }

    log(f"--- [Step {step_counter}] Running SCF with QE ({len(atoms)} atoms) | {query_rtx5080_status()} ---")

    t0 = time.time()
    profile = EspressoProfile(command=command_str, pseudo_dir="./")
    calc = Espresso(profile=profile, pseudopotentials=cfg['pseudopotentials'], input_data=input_data, kpts=cfg['kpts'])
    atoms.calc = calc

    pe_ev = atoms.get_potential_energy()
    forces_ev_angstrom = atoms.get_forces()
    elapsed = time.time() - t0

    # 各ステップの espresso.pwo を履歴ファイルにも追記保存（全ステップの Total force / SCF correction 追跡用）
    if os.path.exists("espresso.pwo"):
        with open("espresso.pwo", "r", encoding="utf-8", errors="ignore") as f_in:
            pwo_text = f_in.read()
        with open("espresso_all_steps.pwo", "a", encoding="utf-8") as f_out:
            f_out.write(f"\n=== STEP {step_counter} ===\n")
            f_out.write(pwo_text)

    fmax_ev_ang = float(np.max(np.linalg.norm(forces_ev_angstrom, axis=1)))
    qm_pe = pe_ev * ev_to_hartree
    qm_forces = forces_ev_angstrom * force_conv

    # auto_generate_progression_graphs.py 互換フォーマットでログ出力
    log(
        f"--- Step Done in {elapsed:.2f}s! Total Energy: {pe_ev:.4f} eV "
        f"({qm_pe:.6f} Hartree) | Fmax: {fmax_ev_ang:.5f} eV/A | {query_rtx5080_status()} ---"
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


if __name__ == "__main__":
    configure_rtx5080_environment()

    args = sys.argv
    mdi_option = ""
    iarg = 1
    while iarg < len(args):
        if args[iarg] in ["-mdi", "--mdi"]:
            if iarg + 1 < len(args):
                mdi_option = args[iarg + 1]
                break
        iarg += 1

    if not mdi_option:
        error("Missing -mdi argument on command line")

    log(f"Initializing MDI Engine (RTX 5080 / Ultra 9 285K) with options: {mdi_option}")
    log(query_rtx5080_status())
    mdi.MDI_Init(mdi_option)

    mdi.MDI_Register_Node("@DEFAULT")
    for cmd in ["EXIT", ">NATOMS", ">CELL", ">ELEMENTS", ">TYPES", ">COORDS", "<ENERGY", "<PE", "<FORCES"]:
        mdi.MDI_Register_Command("@DEFAULT", cmd)

    log("Waiting for MDI driver connection...")
    mdicomm = mdi.MDI_Accept_Communicator()
    log("Connected to MDI driver! Entering communication loop...")

    while not exitflag:
        command = mdi.MDI_Recv_Command(mdicomm)
        execute_command(command, mdicomm, None)

    # 全ステップ履歴があれば espresso.pwo に統合して auto_generate_progression_graphs.py が全点読めるようにする
    if os.path.exists("espresso_all_steps.pwo"):
        shutil.copyfile("espresso_all_steps.pwo", "espresso.pwo")

    log("MDI Engine execution terminated cleanly.")

