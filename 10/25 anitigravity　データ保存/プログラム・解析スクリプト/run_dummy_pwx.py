import pexpect
import sys

with open("run_dummy_pwx.log", "w") as f:
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no colab "cat << \'INEOF\' > /content/SiC_3x3x10_MD/dummy.pwi\n&CONTROL\n  calculation = \'scf\'\n  pseudo_dir = \'./\'\n  outdir = \'./tmp\'\n/\n&SYSTEM\n  ibrav = 0\n  nat = 2\n  ntyp = 2\n  ecutwfc = 40.0\n/\n&ELECTRONS\n/\nATOMIC_SPECIES\n Si 28.085 Si.upf\n C 12.011 C.upf\nCELL_PARAMETERS angstrom\n 10.0 0.0 0.0\n 0.0 10.0 0.0\n 0.0 0.0 10.0\nATOMIC_POSITIONS angstrom\n Si 0.0 0.0 0.0\n C 1.0 1.0 1.0\nINEOF\ncd /content/SiC_3x3x10_MD && export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi; export OPAL_DATADIR=$OPAL_PREFIX/share; export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/mpi/lib:$LD_LIBRARY_PATH; /content/bin/pw.x < dummy.pwi > dummy.pwo 2>&1; cat dummy.pwo"', encoding='utf-8')
    child.logfile_read = f
    index = child.expect(['password:', pexpect.EOF], timeout=10)
    if index == 0:
        child.sendline('mypassword')
        child.expect(pexpect.EOF, timeout=60)
