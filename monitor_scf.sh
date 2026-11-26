#!/bin/bash
while true; do
    ssh colab "grep -E 'iteration #|estimated scf|total energy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 30" > /home/yamazaki_yuta/scf_convergence.log
    sleep 60
done
