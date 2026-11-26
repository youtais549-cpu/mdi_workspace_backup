#!/usr/bin/env python3
"""
==============================================================================
Quantum ESPRESSO + MDI 連成エンジン (Step 0..600 完全キャッシュ復元 & Step 601..900 波動関数・電荷密度引き継ぎ版)
==============================================================================
・Step 0 ～ 600 は prev_600steps_espresso_all_steps.pwo から ASE パーサーで完全復元して即座に返却
・Step 601 以降は ./tmp/pwscf.save 内の Step 600 収束済み波動関数 (wfc1.hdf5) と
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


def load_cached_600_steps():
    global cached_steps
    cache_file = "prev_600steps_espresso_all_steps.pwo"
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
        n_it = int(m_it.group(1)) if m_it else 16
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

    # Step 0..600: Exact cache replay to restore positions, velocities, and Nosé-Hoover chain variables
    if step_counter in cached_steps:
        pe_ev, forces_ev_angstrom, n_scf_iters, pwo_text = cached_steps[step_counter]
        with open("espresso_all_steps.pwo", "a", encoding="utf-8") as f_out:
            f_out.write(f"\n=== STEP {step_counter} ===\n")
            f_out.write(pwo_text)
        if step_counter == 600:
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

    # Step 601..900: Live Quantum ESPRESSO GPU SCF calculation inheriting wfc1.hdf5 & charge-density.hdf5
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
    load_cached_600_steps()
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
