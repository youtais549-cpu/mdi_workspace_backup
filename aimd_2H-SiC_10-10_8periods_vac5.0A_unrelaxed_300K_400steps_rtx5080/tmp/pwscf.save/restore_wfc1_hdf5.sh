#!/bin/bash
cd "$(dirname "$0")"
if [ ! -f wfc1.hdf5 ] && ls wfc1.hdf5.gz.part_* >/dev/null 2>&1; then
    cat wfc1.hdf5.gz.part_* | gunzip > wfc1.hdf5
    echo "Restored wfc1.hdf5 successfully!"
fi
