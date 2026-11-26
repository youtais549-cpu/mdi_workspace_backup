#!/bin/bash
echo "Monitoring SCF convergence from Colab..."
echo "Press Ctrl+C to stop."
while true; do
    date '+[%Y-%m-%d %H:%M:%S]' >> scf_convergence.log
    ssh colab "grep -E 'iteration|estimated scf accuracy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 10" >> scf_convergence.log 2>/dev/null
    echo "Updated scf_convergence.log. Waiting 60 seconds..."
    sleep 60
done
