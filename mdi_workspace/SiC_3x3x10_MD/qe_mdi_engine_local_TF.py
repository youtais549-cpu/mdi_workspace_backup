#!/usr/bin/env python3
import sys
import os
import time
import numpy as np
import mdi
from ase import Atoms
from ase.calculators.espresso import Espresso, EspressoProfile

# 元素シンボルと原子番号のマッピング
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
type_to_symbol = {1: 'Si', 2: 'C'}  # >TYPES用の予備フォールバック

# MDIの状態を保持するグローバル変数
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
    print(f"[QE-MDI Engine] {msg}", flush=True)

def error(txt):
    log(f"ERROR: {txt}")
    sys.exit(1)

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
    if ierr: error("MDI: >CELL data reception failed")
    log("Received >CELL box information.")

def receive_qm_coords(mdicomm):
    if not qm_natoms: error("Cannot receive >COORDS if # of QM atoms = 0")
    ierr = mdi.MDI_Recv(3 * qm_natoms, mdi.MDI_DOUBLE, mdicomm, buf=qm_coords)
    if ierr: error("MDI: >COORDS data reception failed")

def receive_qm_elements(mdicomm):
    if not qm_natoms: error("Cannot receive >ELEMENTS if # of QM atoms = 0")
    ierr = mdi.MDI_Recv(qm_natoms, mdi.MDI_INT, mdicomm, buf=qm_elements)
    if ierr: error("MDI: >ELEMENTS data reception failed")
    symbols = [atomic_number_to_symbol.get(int(a), f'X{a}') for a in qm_elements]
    log(f"Received >ELEMENTS: {symbols}")

def receive_qm_types(mdicomm):
    if not qm_natoms: error("Cannot receive >TYPES if # of QM atoms = 0")
    types = np.empty(qm_natoms, dtype=np.int32)
    ierr = mdi.MDI_Recv(qm_natoms, mdi.MDI_INT, mdicomm, buf=types)
    if ierr: error("MDI: >TYPES data reception failed")
    # atomic number に変換
    for i, t in enumerate(types):
        sym = type_to_symbol.get(int(t), 'Si')
        qm_elements[i] = ELEMENTS.index(sym) + 1
    symbols = [atomic_number_to_symbol.get(int(a), f'X{a}') for a in qm_elements]
    log(f"Received >TYPES mapped to elements: {symbols}")

def evaluate():
    global qm_pe, qm_forces, last_evaluated_coords
    
    if qm_natoms == 0 or qm_elements is None or qm_coords is None:
        error("QM system atoms, elements, or coordinates not fully specified before calculation")

    # 前回の計算と座標が全く同じ場合、再計算せず既存のエネルギー・力を即返却する
    if last_evaluated_coords is not None and np.array_equal(qm_coords, last_evaluated_coords):
        return

    bohr_to_angstrom = mdi.MDI_Conversion_factor("bohr", "angstrom")
    ev_to_hartree = mdi.MDI_Conversion_factor("electron_volt", "hartree")
    force_conv = ev_to_hartree * bohr_to_angstrom  # eV/Angstrom -> Hartree/Bohr

    coords_angstrom = qm_coords * bohr_to_angstrom
    symbols = [atomic_number_to_symbol[int(anum)] for anum in qm_elements]
    
    if flag_box and np.linalg.norm(box) > 1e-6:
        cell_matrix_bohr = box.reshape(3, 3)
        cell_matrix_angstrom = cell_matrix_bohr * bohr_to_angstrom
        pbc = [True, True, True]
    else:
        cell_matrix_angstrom = np.eye(3) * 10.0
        pbc = [True, True, True]

    # Strip MPI env vars to prevent OpenMPI conflicts in subprocess
    for k in list(os.environ.keys()):
        if k.startswith("OMPI_") or k.startswith("PMIX_") or k.startswith("ORTE_"):
            del os.environ[k]

    atoms = Atoms(symbols=symbols, positions=coords_angstrom, cell=cell_matrix_angstrom, pbc=pbc)
    
    log(f"--- Evaluating QM step with Quantum ESPRESSO via ASE ({len(atoms)} atoms: {symbols}) ---")

    # 自分でコンパイルした安定版 QE 7.3 を使用
    pw_bin = '/content/bin/pw.x'

    pseudopotentials = {
        'Si': 'Si.upf',
        'C': 'C.upf'
    }
    input_data = {
        'control': {
            'calculation': 'scf',
            'pseudo_dir': './',
            'outdir': './tmp',
            'tprnfor': True,
            'tstress': True,
            'disk_io': 'none'
        },
        'system': {
            'ecutwfc': 25.0,
            'occupations': 'smearing',
            'smearing': 'gaussian',
            'degauss': 0.01
        },
        'electrons': {
            'conv_thr': 1.0e-5,
            'mixing_beta': 0.6,
            'mixing_mode': 'local-TF',
            'mixing_ndim': 4,
            'electron_maxstep': 200
        }
    }

    pw_bin = "/content/bin/pw.x.serial"
    nvhpc_lib = "/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/math_libs/lib64:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/cuda/lib64:/usr/local/cuda/lib64:/usr/lib64-nvidia"
    command_str = f"env LD_LIBRARY_PATH={nvhpc_lib}:$LD_LIBRARY_PATH {pw_bin} -ndiag 1"
    log(f"Executing ASE with command: {command_str}")
    profile = EspressoProfile(command=command_str, pseudo_dir="./")
    calc = Espresso(profile=profile, pseudopotentials=pseudopotentials, input_data=input_data, kpts=None)
    atoms.calc = calc
    
    pe_ev = atoms.get_potential_energy()
    forces_ev_angstrom = atoms.get_forces()
    
    qm_pe = pe_ev * ev_to_hartree
    qm_forces = forces_ev_angstrom * force_conv
    
    log(f"--- Step Complete! Total Energy: {pe_ev:.4f} eV ({qm_pe:.6f} Hartree) ---")

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
        if ierr: error("MDI: <ENERGY/<PE send failed")
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

    log(f"Initializing MDI Engine with options: {mdi_option}")
    mdi.MDI_Init(mdi_option)
    
    mdi.MDI_Register_Node("@DEFAULT")
    mdi.MDI_Register_Command("@DEFAULT", "EXIT")
    mdi.MDI_Register_Command("@DEFAULT", ">NATOMS")
    mdi.MDI_Register_Command("@DEFAULT", ">CELL")
    mdi.MDI_Register_Command("@DEFAULT", ">ELEMENTS")
    mdi.MDI_Register_Command("@DEFAULT", ">TYPES")
    mdi.MDI_Register_Command("@DEFAULT", ">COORDS")
    mdi.MDI_Register_Command("@DEFAULT", "<ENERGY")
    mdi.MDI_Register_Command("@DEFAULT", "<PE")
    mdi.MDI_Register_Command("@DEFAULT", "<FORCES")

    log("Waiting for MDI driver connection...")
    mdicomm = mdi.MDI_Accept_Communicator()
    log("Connected to MDI driver! Entering communication loop...")

    mdi.MDI_Set_Execute_Command_Func(execute_command, None)
    while not exitflag:
        command = mdi.MDI_Recv_Command(mdicomm)
        execute_command(command, mdicomm, None)
        
    log("MDI Engine execution terminated cleanly.")
