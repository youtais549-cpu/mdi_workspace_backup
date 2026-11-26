#!/bin/bash
HPCX_INIT=$(find /opt/nvidia/hpc_sdk/Linux_x86_64 -name "hpcx-init.sh" 2>/dev/null | sort -V | tail -n 1)
if [ -n "$HPCX_INIT" ] && [ -f "$HPCX_INIT" ]; then
    source "$HPCX_INIT"
    hpcx_load
fi
export TMPDIR=/tmp/pw_hpcx_tmp
mkdir -p "$TMPDIR"
export OMPI_MCA_orte_tmpdir_base="$TMPDIR"
exec mpirun --allow-run-as-root --mca orte_tmpdir_base "$TMPDIR" -np 1 /content/bin/pw.x.real "$@"
