#!/usr/bin/env python3
import re
import csv
import os

# 1. 中断前と再開後の qe_engine.log から全エネルギーを抽出
inter_log = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_intermediate/qe_engine.log"
resume_log = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_relaxed_20261022/qe_engine.log"

evaluations = []

def parse_qe_log(log_path, offset_eval=0):
    evals = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r"Step Done in ([\d\.]+)s! Total Energy: ([-\d\.]+) eV \(([-\d\.]+) Hartree\)", line)
            if m:
                elapsed = float(m.group(1))
                energy_ev = float(m.group(2))
                energy_ha = float(m.group(3))
                evals.append({
                    "eval_no": len(evals) + 1 + offset_eval,
                    "elapsed_sec": elapsed,
                    "energy_ev": energy_ev,
                    "energy_hartree": energy_ha
                })
    return evals

inter_evals = parse_qe_log(inter_log, 0)
resume_evals = parse_qe_log(resume_log, len(inter_evals))
all_evals = inter_evals + resume_evals

print(f"Total QE Evaluations extracted: {len(all_evals)} (Intermediate: {len(inter_evals)}, Resume: {len(resume_evals)})")

# 2. LAMMPS の log.lammps から確定ステップの TotEng を抽出
inter_lammps = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_intermediate/log.lammps"
resume_lammps = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_relaxed_20261022/log.lammps"

lammps_steps = []
def parse_lammps(log_path, offset_step=0):
    steps = []
    in_thermo = False
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Step" in line and "TotEng" in line:
                in_thermo = True
                continue
            if in_thermo:
                parts = line.split()
                if len(parts) >= 5 and parts[0].isdigit():
                    step_num = int(parts[0])
                    tot_eng = float(parts[4])
                    steps.append({
                        "step": step_num + offset_step,
                        "tot_eng_ev": tot_eng
                    })
                elif "Loop time" in line or "ERROR" in line or "Minimization stats" in line:
                    in_thermo = False
    return steps

inter_steps = parse_lammps(inter_lammps, 0)
max_inter_step = inter_steps[-1]["step"] if inter_steps else 0
resume_steps = parse_lammps(resume_lammps, max_inter_step + 1)
all_lammps_steps = inter_steps + resume_steps
print(f"Total LAMMPS steps extracted: {len(all_lammps_steps)} (Inter: {len(inter_steps)}, Resume: {len(resume_steps)})")

# CSV 出力
csv_path = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_relaxed_20261022/energy_progression.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Evaluation_No", "Elapsed_Sec", "Total_Energy_eV", "Total_Energy_Hartree"])
    for e in all_evals:
        writer.writerow([e["eval_no"], e["elapsed_sec"], e["energy_ev"], e["energy_hartree"]])

csv_lammps = "/home/yamazaki/mdi_workspace_backup/results_2H-SiC_10-10_slab_4periods_vac5A_relaxed_20261022/lammps_steps_energy.csv"
with open(csv_lammps, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["LAMMPS_Step", "TotEng_eV"])
    for s in all_lammps_steps:
        writer.writerow([s["step"], s["tot_eng_ev"]])

print(f"CSVs saved: {csv_path}, {csv_lammps}")
