#!/usr/bin/env python3
"""
==============================================================================
Quantum ESPRESSO + MDI 連成コアエンジン (T4 GPU 最適化版)
【固定コアコード: ユーザー編集不要】
==============================================================================
・MDIプロトコルによるLAMMPSとのTCPソケット通信制御
・T4 GPU (OpenACC / CUDA CC 75) 向けライブラリ環境の自動検出
・ASE EspressoProfile ラッパー経由での GPU pw.x 呼び出し
・dft_settings.py からの動的パラメータ読み込み
"""
import sys
import os
import glob
import time
import numpy as np
import mdi
from ase import Atoms
from ase.calculators.espresso import Espresso, EspressoProfile
import ase.parallel
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
atomic_number_to_symbol = {i+1: symbol for i, symbol in enumerate(ELEMENTS)}
type_to_symbol = {1: 'C', 2: 'Si'}  # ASEアルファベット順 (Type 1: C, Type 2: Si)

exitflag = False
qm_natoms = 0
qm_elements = None
qm_coords = None
box = np.zeros(9, dtype=np.float64)
flag_box = False

qm_pe = 0.0
qm_forces = None
last_evaluated_coords = None

def log(msg):
    print(f"[QE-MDI Core Engine] {msg}", flush=True)

def error(txt):
    log(f"ERROR: {txt}")
    sys.exit(1)

def load_dft_config():
    """外部の dft_settings.py からDFT条件を動的に読み込み（なければデフォルト）"""
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
        'pseudopotentials': {'Si': 'Si.upf', 'C': 'C.upf'}
    }
    try:
        if os.path.exists("dft_settings.py"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("dft_settings", "dft_settings.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'DFT_CONFIG'):
                default_config.update(mod.DFT_CONFIG)
                log("Successfully loaded customized DFT_CONFIG from dft_settings.py")
    except Exception as e:
        log(f"Notice: Using default DFT parameters ({e})")
    return default_config

def find_nvhpc_and_pw():
    """NVHPCライブラリパスおよびGPU版pw.xバイナリの自動検出"""
    nvhpc_roots = glob.glob("/opt/nvidia/hpc_sdk/Linux_x86_64/*")
    nvhpc_libs = []
    if nvhpc_roots:
        nvhpc_roots.sort(reverse=True)
        root = nvhpc_roots[0]
        nvhpc_libs = [
            f"{root}/compilers/lib",
            f"{root}/math_libs/lib64",
            f"{root}/cuda/lib64",
            f"{root}/comm_libs/mpi/lib"
        ]
        hpcx_libs = glob.glob(f"{root}/comm_libs/*/hpcx/*/ompi/lib")
        nvhpc_libs.extend(hpcx_libs)
        log(f"Detected NVHPC SDK at: {root}")
    
    cuda_libs = [
        "/usr/local/cuda/lib64",
        "/usr/lib64-nvidia",
        "/usr/local/nvidia/lib",
        "/usr/local/nvidia/lib64",
        "/usr/lib/x86_64-linux-gnu"
    ]
    all_libs = [p for p in (nvhpc_libs + cuda_libs) if os.path.exists(p)]
    ld_path_str = ":".join(all_libs)
    
    candidates = [
        "/content/bin/pw.x.gpu",
        "/content/bin/pw.x.serial",
        "/content/q-e/build_gpu_serial/bin/pw.x",
        "/content/q-e/build/bin/pw.x",
        "/content/bin/pw.x",
        "/content/drive/MyDrive/mdi_binaries/pw.x",
        "pw.x"
    ]
    pw_bin = None
    for cand in candidates:
        if os.path.exists(cand) and os.access(cand, os.X_OK):
            pw_bin = cand
            break
    if not pw_bin:
        pw_bin = "/content/bin/pw.x"
    log(f"Using Quantum ESPRESSO binary: {pw_bin}")
    return pw_bin, ld_path_str

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
    if ierr: error("MDI: >CELL reception failed")

def receive_qm_coords(mdicomm):
    if not qm_natoms: error("Cannot receive >COORDS if # atoms = 0")
    ierr = mdi.MDI_Recv(3 * qm_natoms, mdi.MDI_DOUBLE, mdicomm, buf=qm_coords)
    if ierr: error("MDI: >COORDS reception failed")

def receive_qm_elements(mdicomm):
    if not qm_natoms: error("Cannot receive >ELEMENTS if # atoms = 0")
    ierr = mdi.MDI_Recv(qm_natoms, mdi.MDI_INT, mdicomm, buf=qm_elements)
    if ierr: error("MDI: >ELEMENTS reception failed")

def receive_qm_types(mdicomm):
    if not qm_natoms: error("Cannot receive >TYPES if # atoms = 0")
    types = np.empty(qm_natoms, dtype=np.int32)
    ierr = mdi.MDI_Recv(qm_natoms, mdi.MDI_INT, mdicomm, buf=types)
    if ierr: error("MDI: >TYPES reception failed")
    for i, t in enumerate(types):
        sym = type_to_symbol.get(int(t), 'C')
        qm_elements[i] = ELEMENTS.index(sym) + 1

def evaluate():
    global qm_pe, qm_forces, last_evaluated_coords
    if qm_natoms == 0 or qm_elements is None or qm_coords is None:
        error("System atoms, elements, or coordinates not fully specified")

    # 座標キャッシュ: 同一ステップでの重複SCF計算を防止
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
    pw_bin, _ = find_nvhpc_and_pw()
    cfg = load_dft_config()
    
    input_data = {
        'control': {
            'calculation': 'scf',
            'pseudo_dir': './',
            'outdir': './tmp',
            'tprnfor': True,
            'tstress': True,
            'disk_io': 'minimal'
        },
        'system': {
            'ecutwfc': cfg['ecutwfc'],
            'ecutrho': cfg['ecutrho'],
            'occupations': cfg['occupations'],
            'smearing': cfg['smearing'],
            'degauss': cfg['degauss']
        },
        'electrons': {
            'conv_thr': cfg['conv_thr'],
            'mixing_beta': cfg['mixing_beta'],
            'mixing_mode': cfg['mixing_mode'],
            'electron_maxstep': cfg['electron_maxstep']
        }
    }

    command_str = f"{pw_bin} -ndiag 1"
    log(f"--- Running GPU SCF calculation with QE ({len(atoms)} atoms) ---")
    
    t0 = time.time()
    profile = EspressoProfile(command=command_str, pseudo_dir="./")
    calc = Espresso(profile=profile, pseudopotentials=cfg['pseudopotentials'], input_data=input_data, kpts=cfg['kpts'])
    atoms.calc = calc
    
    pe_ev = atoms.get_potential_energy()
    forces_ev_angstrom = atoms.get_forces()
    elapsed = time.time() - t0
    
    qm_pe = pe_ev * ev_to_hartree
    qm_forces = forces_ev_angstrom * force_conv
    
    log(f"--- Step Done in {elapsed:.2f}s! Total Energy: {pe_ev:.4f} eV ({qm_pe:.6f} Hartree) ---")
    last_evaluated_coords = np.copy(qm_coords)

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
        if ierr: error("MDI: <ENERGY send failed")
    elif command == "<FORCES":
        evaluate()
        ierr = mdi.MDI_Send(qm_forces, 3 * qm_natoms, mdi.MDI_DOUBLE, mdicomm)
        if ierr: error("MDI: <FORCES send failed")
    else:
        error(f"Unrecognized MDI command: {command}")
    return 0

if __name__ == "__main__":
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

    log(f"Initializing MDI Core Engine with options: {mdi_option}")
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
        
    log("MDI Core Engine execution terminated cleanly.")
