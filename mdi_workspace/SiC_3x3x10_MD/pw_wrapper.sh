#!/bin/bash
# Unset OpenMPI and PMIX environment variables that leaked from the parent mpirun
unset $(env | grep -Eo '^OMPI_[^=]+|^PMIX_[^=]+|^OPAL_[^=]+|^ORTE_[^=]+')

# Set required library paths for NVHPC
export LD_LIBRARY_PATH="/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/compilers/lib:/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/cuda/lib64:$LD_LIBRARY_PATH"

# Run pw.x using mpirun
/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi/bin/mpirun --allow-run-as-root -np 1 /content/bin/pw.x "$@"
