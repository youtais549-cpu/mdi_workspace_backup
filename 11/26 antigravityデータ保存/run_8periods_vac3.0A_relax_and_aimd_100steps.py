#!/usr/bin/env python3
r"""
run_8periods_vac3.0A_relax_and_aimd_100steps.py
==============================================================================
2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 3.0 Å (スラブ間ギャップ 6.0 Å)
  Phase 1: 8周期・真空5.0Å緩和済み構造から真空層を 5.0Å → 3.0Å に詰めたモデルの 0 K 構造最適化
  Phase 2: 0 K 緩和済み構造を初期構造とした 300 K NVT 第一原理分子動力学 (AIMD 100 steps = 100 fs)

【検証目的】:
  ① 発散せずに計算が回るか (各ステップのSCF収束、全エネルギー・温度 T ≈ 300 K の安定推移)
  ② 真空層 3.0 Å (スラブ間ギャップ 6.0 Å) で隣接スラブとぶつからないか
     (300 K の MD 中における最表面原子の Z 座標の最大変位・熱振動振幅 [Å] と最小ギャップの実測)
  ③ startingpot = 'file', startingwfc = 'file' (disk_io = 'medium') による波動関数・電荷密度引き継ぎの有効化
==============================================================================
"""

import os
import sys
import re
import json
import time
import shutil
import datetime
import subprocess
import numpy as np

WORKSPACE_DIR = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup"
ENV_PREFIX = "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_env_rtx5080"
TEMPLATE_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_8periods_vac5A_natural_cleavage")

RELAX_DIR = os.path.join(WORKSPACE_DIR, "calc_2H-SiC_10-10_8periods_vac3.0A_rtx5080")
AIMD_DIR = os.path.join(WORKSPACE_DIR, "aimd_2H-SiC_10-10_8periods_vac3.0A_300K_100steps_rtx5080")

LOG_FILE = os.path.join(WORKSPACE_DIR, "aimd_8periods_vac3.0A_run.log")

# 8周期 (288原子) 真のバルク基準エネルギー (確定済み)
TRUE_BULK_ENERGY_RY = -9387.69989164
TRUE_BULK_ENERGY_EV = -127726.1628
AREA_2A = 279.497664
CONV_FACTOR = 16.021766
EFFECTIVE_DENOM = AREA_2A / CONV_FACTOR  # 17.44487243166577


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def create_vac3A_data_from_vac5A_relaxed(src_data_path, dst_data_path):
    """
    8周期・真空5.0Åの緩和済みLAMMPSデータファイル (slab_10-10_288atoms_vac5A_relaxed.data) から
    真空層部分のみを 5.0 Å → 3.0 Å に詰めた LAMMPS データファイルを生成する。
    ・セル高さ Lz: 29.53540130124298 Å → 25.53540130124298 Å (-4.0 Å)
    ・全原子の z 座標: z → z - 2.0 Å (下部真空 5.0→3.0 Å, 上部真空 5.0→3.0 Å)
    ・スラブ内部の相対座標・結合長・表面再構成構造は 100% 完全保持
    ・image flags (ix, iy, iz) は 0 0 0 にリセットし、Velocities セクションは除去
    """
    with open(src_data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out_lines = []
    in_atoms = False
    in_velocities = False
    z_vals = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Velocities"):
            in_atoms = False
            in_velocities = True
            continue
        if in_velocities:
            continue

        if "zlo zhi" in stripped:
            parts = stripped.split()
            zlo = float(parts[0])
            zhi = float(parts[1]) - 4.0  # 29.53540130124298 -> 25.53540130124298
            out_lines.append(f"{zlo:.1f} {zhi:.14f} zlo zhi\n")
            continue

        if stripped.startswith("Atoms"):
            in_atoms = True
            out_lines.append("Atoms # atomic\n\n")
            continue

        if in_atoms:
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) >= 5 and parts[0].isdigit():
                aid = int(parts[0])
                atype = int(parts[1])
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4]) - 2.0  # Shift z by -2.0 Å
                z_vals.append((aid, atype, x, y, z))
            continue

        out_lines.append(line)

    # Sort by Atom ID (Rule 2: 原子IDでソート)
    z_vals.sort(key=lambda item: item[0])
    for aid, atype, x, y, z in z_vals:
        out_lines.append(f"{aid:6d} {atype:3d} {x:20.14f} {y:20.14f} {z:20.14f}\n")

    with open(dst_data_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    z_arr = np.array([item[4] for item in z_vals])
    log(
        f"Created {os.path.basename(dst_data_path)}: {len(z_vals)} atoms, "
        f"z_min={z_arr.min():.4f} Å, z_max={z_arr.max():.4f} Å, Lz={zhi:.6f} Å "
        f"(initial inter-slab gap = {(z_arr.min() + zhi) - z_arr.max():.4f} Å)"
    )


def write_qe_mdi_engine_with_wfc_extrapolation(dst_dir):
    """
    startingpot = 'file', startingwfc = 'file' (および disk_io = 'medium') を有効化し、
    前ステップの収束済み波動関数・電荷密度を次ステップの初期推測に引き継ぐ QE-MDI エンジンを作成
    """
    engine_code = r'''#!/usr/bin/env python3
"""
==============================================================================
Quantum ESPRESSO + MDI 連成エンジン (波動関数・電荷密度引き継ぎ高速化対応版)
==============================================================================
・2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 3.0 Å
・startingpot = 'file', startingwfc = 'file', disk_io = 'medium' を有効化し、
  前のステップで収束した波動関数・電荷密度を次ステップの初期推測として引き継ぐ
・ASE + MDI DummyMPI 適用 (AGENTS.md §3)
・Type 1 = C (12.011), Type 2 = Si (28.085) 厳格一致 (AGENTS.md §2)
"""
import sys
import os
import re
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
    print(f"[QE-MDI Engine] {msg}", flush=True)


def error(txt):
    log(f"ERROR: {txt}")
    sys.exit(1)


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
    """./tmp/pwscf.save 内に前ステップの電荷密度と波動関数ファイルが存在するか確認"""
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
            'disk_io': 'medium',  # 波動関数 (wfc1.hdf5) と電荷密度 (charge-density.hdf5) を保存して次ステップへ引き継ぐ
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

    z_coords = coords_angstrom[:, 2]
    Lz = cell_matrix_angstrom[2, 2]
    z_min, z_max = float(np.min(z_coords)), float(np.max(z_coords))
    current_gap = (z_min + Lz) - z_max

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
    mdi_options = None
    for i, arg in enumerate(sys.argv):
        if arg in ["-mdi", "--mdi"] and i + 1 < len(sys.argv):
            mdi_options = sys.argv[i + 1]
            break
    if not mdi_options:
        error("MDI options not provided. Use -mdi '-role ENGINE -name QE -method TCP -port 8029 -hostname localhost'")

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
    engine_path = os.path.join(dst_dir, "qe_mdi_engine_rtx5080.py")
    with open(engine_path, "w", encoding="utf-8") as f:
        f.write(engine_code)
    os.chmod(engine_path, 0o755)


def deploy_common_assets(dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for asset in [
        "C.upf",
        "Si.upf",
        "RELAXATION_GRAPH_PROTOCOL.json",
        "dft_settings.py",
        "make_xyz.py",
        "msmincho.ttc",
        "times.ttf",
        "auto_generate_progression_graphs.py",
    ]:
        src = os.path.join(TEMPLATE_DIR, asset)
        dst = os.path.join(dst_dir, asset)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copyfile(src, dst)
    write_qe_mdi_engine_with_wfc_extrapolation(dst_dir)


def run_phase1_0K_relaxation():
    """
    Phase 1: 8周期・真空5.0Åの緩和済み構造から真空層を 3.0Å に詰めたモデルの 0 K 構造最適化
    """
    log("==============================================================================")
    log("Phase 1: Starting 0 K Structural Optimization for 8-period Vac 3.0 Å Slab")
    log("==============================================================================")

    deploy_common_assets(RELAX_DIR)

    src_relaxed_5A = os.path.join(TEMPLATE_DIR, "slab_10-10_288atoms_vac5A_relaxed.data")
    init_3A_data = os.path.join(RELAX_DIR, "slab_10-10_288atoms_vac3.0A_init.data")
    relaxed_3A_data = os.path.join(RELAX_DIR, "slab_10-10_288atoms_vac3.0A_relaxed.data")

    create_vac3A_data_from_vac5A_relaxed(src_relaxed_5A, init_3A_data)

    # Write LAMMPS input for 0 K CG relaxation (Rule 9: minimize 1.0e-6 1.0e-2 100 150)
    in_lammps_relax = """# ==============================================================================
# 2H-SiC {10-10} 8周期 (16層, 288原子) 真空層 3.0 Å スラブ 0 K 構造緩和
# (8周期・真空5.0Å緩和済み構造から真空層を 5.0Å → 3.0Å に詰めた初期構造の微調整緩和)
# ==============================================================================
units           metal
dimension       3
boundary        p p p
atom_style      atomic
atom_modify     map yes

read_data       slab_10-10_288atoms_vac3.0A_init.data

# Rule 2: Type 1 = C (12.011), Type 2 = Si (28.085)
mass            1 12.011
mass            2 28.085

pair_style      none

fix             1 all mdi/qm elements C Si
thermo_style    custom step temp pe etotal press fmax fnorm
thermo          1
thermo_modify   flush yes

dump            1 all custom 1 dump.lammpstrj id type x y z fx fy fz
dump_modify     1 sort id flush yes

# Rule 9: 最適化収束条件標準
min_style       cg
minimize        1.0e-6 1.0e-2 100 150

write_data      slab_10-10_288atoms_vac3.0A_relaxed.data
"""
    with open(os.path.join(RELAX_DIR, "in.lammps.optimized_conv"), "w", encoding="utf-8") as f:
        f.write(in_lammps_relax)
    with open(os.path.join(RELAX_DIR, "in.lammps"), "w", encoding="utf-8") as f:
        f.write(in_lammps_relax)

    # Clean previous logs if any
    for fn in ["dump.lammpstrj", "log.lammps", "lmp.log", "qe_engine.log", "espresso.pwo", "espresso_all_steps.pwo"]:
        p = os.path.join(RELAX_DIR, fn)
        if os.path.exists(p):
            os.remove(p)

    port = 8038
    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["QE_MPI_NP"] = "12"
    env["QE_OMP_THREADS"] = "2"

    lmp_bin = os.path.join(ENV_PREFIX, "bin", "lmp")
    py_bin = os.path.join(ENV_PREFIX, "bin", "python3")

    t0 = time.time()
    lmp_log_f = open(os.path.join(RELAX_DIR, "lmp.log"), "w")
    qe_log_f = open(os.path.join(RELAX_DIR, "qe_engine.log"), "w")

    lmp_proc = subprocess.Popen(
        [lmp_bin, "-mdi", f"-role DRIVER -name LAMMPS -method TCP -port {port}", "-in", "in.lammps.optimized_conv", "-log", "log.lammps"],
        cwd=RELAX_DIR,
        env=env,
        stdout=lmp_log_f,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    qe_proc = subprocess.Popen(
        [py_bin, "qe_mdi_engine_rtx5080.py", "-mdi", f"-role ENGINE -name QE -method TCP -port {port} -hostname localhost"],
        cwd=RELAX_DIR,
        env=env,
        stdout=qe_log_f,
        stderr=subprocess.STDOUT,
    )

    lmp_proc.wait()
    try:
        qe_proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        qe_proc.kill()

    lmp_log_f.close()
    qe_log_f.close()
    elapsed = time.time() - t0

    if not os.path.exists(relaxed_3A_data):
        raise RuntimeError("Phase 1 failed: slab_10-10_288atoms_vac3.0A_relaxed.data was not produced!")

    # Generate XYZ and progression graphs
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=RELAX_DIR, env=env, check=False)
    subprocess.run([py_bin, "auto_generate_progression_graphs.py"], cwd=RELAX_DIR, env=env, check=False)

    # Parse relaxed energy
    with open(os.path.join(RELAX_DIR, "espresso_all_steps.pwo"), "r", encoding="utf-8", errors="ignore") as f:
        pwo_all = f.read()
    m_e = re.findall(r"!\s+total energy\s+=\s+([-\d\.]+)\s+Ry", pwo_all)
    e_slab_ry = float(m_e[-1])
    e_slab_ev = e_slab_ry * 13.605693122994
    delta_e = e_slab_ev - TRUE_BULK_ENERGY_EV
    gamma = delta_e / EFFECTIVE_DENOM

    meta = {
        "cleavage_plane": "10-10",
        "cleavage_type": "natural_cleavage_sparse_bond",
        "n_periods": 8,
        "n_layers": 16,
        "natoms": 288,
        "vacuum_thickness_angstrom": 3.0,
        "supercell_xy": [3, 3],
        "cell_slab": [9.228, 15.144, 25.53540130124298],
        "cell_bulk": [9.228, 15.144, 21.311153136327466],
        "area_A_angstrom2": 139.748832,
        "total_area_2A_angstrom2": AREA_2A,
        "true_bulk_scf_energy_Ry": TRUE_BULK_ENERGY_RY,
        "true_bulk_scf_energy_eV": TRUE_BULK_ENERGY_EV,
        "relaxed_slab_energy_Ry": round(e_slab_ry, 8),
        "relaxed_slab_energy_eV": round(e_slab_ev, 4),
        "delta_energy_eV": round(delta_e, 4),
        "surface_fracture_energy_J_m2": round(gamma, 4),
        "elapsed_seconds": round(elapsed, 1),
        "n_scf_steps": len(m_e),
    }
    with open(os.path.join(RELAX_DIR, "fracture_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    log(
        f"Phase 1 Completed in {elapsed:.1f}s ({len(m_e)} SCF steps): "
        f"E_slab = {e_slab_ev:.4f} eV, dE = {delta_e:.4f} eV, gamma = {gamma:.4f} J/m^2"
    )
    return relaxed_3A_data


def clean_relaxed_data_for_aimd(src_relaxed_data, dst_aimd_data):
    """
    Phase 1 で出力された slab_10-10_288atoms_vac3.0A_relaxed.data から
    Velocities セクションおよび image flags を整理して AIMD 初期構造ファイルとして保存
    """
    with open(src_relaxed_data, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out_lines = []
    in_atoms = False
    in_velocities = False
    atoms_list = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Velocities"):
            in_atoms = False
            in_velocities = True
            continue
        if in_velocities:
            continue
        if stripped.startswith("Atoms"):
            in_atoms = True
            out_lines.append("Atoms # atomic\n\n")
            continue
        if in_atoms:
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) >= 5 and parts[0].isdigit():
                aid = int(parts[0])
                atype = int(parts[1])
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4])
                atoms_list.append((aid, atype, x, y, z))
            continue
        out_lines.append(line)

    atoms_list.sort(key=lambda item: item[0])
    for aid, atype, x, y, z in atoms_list:
        out_lines.append(f"{aid:6d} {atype:3d} {x:20.14f} {y:20.14f} {z:20.14f}\n")

    with open(dst_aimd_data, "w", encoding="utf-8") as f:
        f.writelines(out_lines)


def run_phase2_300K_aimd_100steps(relaxed_3A_data):
    """
    Phase 2: 0 K 緩和済み構造 (8周期・真空3.0Å) を初期構造とした 300 K NVT-AIMD (100 steps)
    """
    log("==============================================================================")
    log("Phase 2: Starting 300 K NVT AIMD (100 steps = 100 fs) for 8-period Vac 3.0 Å")
    log("==============================================================================")

    deploy_common_assets(AIMD_DIR)

    aimd_init_data = os.path.join(AIMD_DIR, "slab_10-10_288atoms_vac3.0A_relaxed.data")
    clean_relaxed_data_for_aimd(relaxed_3A_data, aimd_init_data)

    # Phase 1 で収束済みの ./tmp (pwscf.save の電荷密度・波動関数) を AIMD_DIR/tmp に引き継ぐことで
    # AIMD の Step 0 から波動関数・電荷密度の再利用を可能にする
    src_tmp = os.path.join(RELAX_DIR, "tmp")
    dst_tmp = os.path.join(AIMD_DIR, "tmp")
    if os.path.exists(src_tmp):
        if os.path.exists(dst_tmp):
            shutil.rmtree(dst_tmp)
        shutil.copytree(src_tmp, dst_tmp)
        log("Copied converged ground-state wavefunctions (./tmp/pwscf.save) from Phase 1 to AIMD directory.")

    in_lammps_aimd = """# ==============================================================================
# 2H-SiC {10-10} 8周期 (16層, 288原子) スラブモデル (真空層 各3.0Å, ギャップ 6.0Å)
# 有限温度第一原理分子動力学 (AIMD: NVT アンサンブル @ 300K, 100 steps = 100 fs)
# ==============================================================================
# 単位系: metal (距離: Å, 時間: ps, エネルギー: eV, 温度: K, 質量: g/mol)
units           metal
dimension       3
boundary        p p p
atom_style      atomic
atom_modify     map yes

# 1. 初期構造の読み込み (8周期・真空3.0Å の 0K 構造最適化済み最安定構造)
read_data       slab_10-10_288atoms_vac3.0A_relaxed.data

# 原子質量設定 (Rule 2: Type 1: C = 12.011, Type 2: Si = 28.085)
mass            1 12.011
mass            2 28.085

pair_style      none

# 2. MDI 通信設定 (Quantum ESPRESSO を第一原理 QM エンジンとして連成)
fix             1 all mdi/qm elements C Si

# 3. 初期熱運動速度の付与 (Maxwell-Boltzmann 分布 @ 300K)
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

# 7. AIMD 実行 (100 steps = 100 fs = 0.1 ps)
run             100

write_data      slab_10-10_288atoms_vac3.0A_aimd_100steps_final.data
undump          1
"""
    with open(os.path.join(AIMD_DIR, "in.lammps"), "w", encoding="utf-8") as f:
        f.write(in_lammps_aimd)

    for fn in ["dump.lammpstrj", "log.lammps", "lmp.log", "qe_engine.log", "espresso.pwo", "espresso_all_steps.pwo"]:
        p = os.path.join(AIMD_DIR, fn)
        if os.path.exists(p):
            os.remove(p)

    port = 8039
    env = os.environ.copy()
    env["PATH"] = f"{ENV_PREFIX}/bin:" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = f"{ENV_PREFIX}/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["OMPI_MCA_btl_vader_single_copy_mechanism"] = "none"
    env["QE_MPI_NP"] = "12"
    env["QE_OMP_THREADS"] = "2"

    lmp_bin = os.path.join(ENV_PREFIX, "bin", "lmp")
    py_bin = os.path.join(ENV_PREFIX, "bin", "python3")

    t0 = time.time()
    lmp_log_f = open(os.path.join(AIMD_DIR, "lmp.log"), "w")
    qe_log_f = open(os.path.join(AIMD_DIR, "qe_engine.log"), "w")

    lmp_proc = subprocess.Popen(
        [lmp_bin, "-mdi", f"-role DRIVER -name LAMMPS -method TCP -port {port}", "-in", "in.lammps", "-log", "log.lammps"],
        cwd=AIMD_DIR,
        env=env,
        stdout=lmp_log_f,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    qe_proc = subprocess.Popen(
        [py_bin, "qe_mdi_engine_rtx5080.py", "-mdi", f"-role ENGINE -name QE -method TCP -port {port} -hostname localhost"],
        cwd=AIMD_DIR,
        env=env,
        stdout=qe_log_f,
        stderr=subprocess.STDOUT,
    )

    lmp_proc.wait()
    try:
        qe_proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        qe_proc.kill()

    lmp_log_f.close()
    qe_log_f.close()
    elapsed = time.time() - t0

    # Winmostar 用アニメーション生成
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_animation.xyz"], cwd=AIMD_DIR, env=env, check=False)
    subprocess.run([py_bin, "make_xyz.py", "dump.lammpstrj", "md_nvt_animation.xyz"], cwd=AIMD_DIR, env=env, check=False)

    log(f"Phase 2 (300 K AIMD 100 steps) Completed in {elapsed:.1f}s ({elapsed/60.0:.1f} min)!")


if __name__ == "__main__":
    try:
        shutil.rmtree("/tmp/test_qe_restart", ignore_errors=True)
        rel_3a = run_phase1_0K_relaxation()
        run_phase2_300K_aimd_100steps(rel_3a)
        log("ALL PHASES COMPLETED SUCCESSFULLY!")
    except Exception as exc:
        log(f"FATAL ERROR: {exc}")
        raise

