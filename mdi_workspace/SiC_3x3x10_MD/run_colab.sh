#!/bin/bash

rm -rf tmp qe.out qe_mdi.pwo qe_mdi.pwi dump.lammpstrj qe_engine.log

echo "Starting LAMMPS MDI driver..."
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
export PMIX_MCA_gds=hash
export OMPI_MCA_btl_vader_single_copy_mechanism=none
/content/bin/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021" -in in.lammps &
LMP_PID=$!


sleep 1

echo "Starting Python QE MDI engine..."
python3 qe_mdi_engine.py -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" 2>&1 | tee qe_engine.log

wait $LMP_PID

echo "Done!"
