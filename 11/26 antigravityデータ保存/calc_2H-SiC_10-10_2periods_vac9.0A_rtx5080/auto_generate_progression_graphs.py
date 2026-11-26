#!/usr/bin/env python3
"""
auto_generate_progression_graphs.py (WORKSTATION4WSL / RTX 5080 新環境対応版)
指示書 (RELAXATION_GRAPH_PROTOCOL.json) に基づき、
計算ログから自動で 3 種の推移グラフ (PNG 600dpi, PDF, SVG) を生成し、
計算成果物ディレクトリおよびバックアップ先へ即時保存する汎用エンジン。
"""

import os
import sys
import re
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker


def find_protocol():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    candidates = [
        "RELAXATION_GRAPH_PROTOCOL.json",
        os.path.join(script_dir, "RELAXATION_GRAPH_PROTOCOL.json"),
        os.path.join(workspace_dir, "RELAXATION_GRAPH_PROTOCOL.json"),
        "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/mdi_workspace_backup/RELAXATION_GRAPH_PROTOCOL.json",
    ]
    for c in candidates:
        if os.path.exists(c):
            with open(c, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None


def parse_logs():
    """qe_engine.log, espresso.pwo (または espresso_all_steps.pwo), log.lammps から推移データを自動抽出"""
    steps = []
    energies = []
    forces = []
    scf_corrections = []

    if os.path.exists("qe_engine.log"):
        with open("qe_engine.log", "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        step_idx = 0
        for line in lines:
            m = re.search(r"Step Done in\s+([\d\.]+)s!\s+Total Energy:\s+([-\d\.]+)\s+eV", line)
            if m:
                e_val = float(m.group(2))
                steps.append(step_idx)
                energies.append(e_val)
                step_idx += 1

    pwo_source = "espresso_all_steps.pwo" if os.path.exists("espresso_all_steps.pwo") else "espresso.pwo"
    if os.path.exists(pwo_source):
        with open(pwo_source, "r", encoding="utf-8", errors="ignore") as f:
            pwo_content = f.read()
        force_matches = re.findall(
            r"Total force\s+=\s+([-\d\.]+)\s+Total SCF correction\s+=\s+([-\d\.]+)",
            pwo_content,
        )
        for f_match in force_matches:
            forces.append(float(f_match[0]))
            scf_corrections.append(float(f_match[1]))

    if len(steps) == 0 and os.path.exists(pwo_source):
        with open(pwo_source, "r", encoding="utf-8", errors="ignore") as f:
            pwo_content = f.read()
        e_matches = re.findall(r"!\s+total energy\s+=\s+([-\d\.]+)\s+Ry", pwo_content)
        for idx, ry_str in enumerate(e_matches):
            steps.append(idx)
            energies.append(float(ry_str) * 13.605693122994)

    if len(steps) == 0:
        raise RuntimeError("No valid SCF step data found in qe_engine.log or espresso.pwo")

    n_pts = min(len(steps), len(forces)) if len(forces) > 0 else len(steps)
    steps = steps[:n_pts]
    energies = energies[:n_pts]
    forces = forces[:n_pts] if len(forces) >= n_pts else forces
    scf_corrections = scf_corrections[:n_pts] if len(scf_corrections) >= n_pts else scf_corrections

    return np.array(steps), np.array(energies), np.array(forces), np.array(scf_corrections)


def get_backup_dir():
    """master_run_rtx5080.sh, master_run_gpu.sh, または fracture_metadata.json から保存先を抽出"""
    for script_name in ["master_run_rtx5080.sh", "master_run_gpu.sh"]:
        if os.path.exists(script_name):
            with open(script_name, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    m = re.search(r'BACKUP_DIR=["\']([^"\']+)["\']', line)
                    if m:
                        return m.group(1)
    if os.path.exists("fracture_metadata.json"):
        try:
            with open("fracture_metadata.json", "r", encoding="utf-8") as f:
                meta = json.load(f)
                if "backup_dir" in meta:
                    return meta["backup_dir"]
        except Exception:
            pass
    return None


def main():
    protocol = find_protocol()
    spec = protocol.get("style_specification", {}) if protocol else {}

    width_in = spec.get("width_cm", 8.0) / 2.54
    height_in = spec.get("height_cm", 6.2) / 2.54
    dpi = spec.get("dpi", 600)
    color = spec.get("line_color", "#8A2BE2")
    marker = spec.get("marker", "^")
    msize = spec.get("marker_size", 45)

    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams['svg.fonttype'] = 'path'
    plt.rcParams['axes.linewidth'] = 1.2
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True

    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)

    font_candidates_mincho = [
        "msmincho.ttc",
        os.path.join(script_dir, "msmincho.ttc"),
        os.path.join(workspace_dir, "msmincho.ttc"),
        os.path.join(workspace_dir, "環境設定・フォント", "msmincho.ttc"),
        os.path.expanduser("~/.local/share/fonts/msmincho.ttc"),
        os.path.expanduser("~/.fonts/msmincho.ttc"),
        "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/msmincho.ttc",
    ]
    msmincho = next((f for f in font_candidates_mincho if os.path.exists(f)), None)

    font_candidates_times = [
        "times.ttf",
        os.path.join(script_dir, "times.ttf"),
        os.path.join(workspace_dir, "times.ttf"),
        os.path.join(workspace_dir, "環境設定・フォント", "times.ttf"),
        os.path.expanduser("~/.local/share/fonts/times.ttf"),
        os.path.expanduser("~/.fonts/times.ttf"),
        "/home/WORKSTATION4WSL/.gemini/antigravity/scratch/times.ttf",
    ]
    times = next((f for f in font_candidates_times if os.path.exists(f)), None)

    font_label = fm.FontProperties(fname=msmincho, size=10.5) if msmincho else fm.FontProperties(size=10.5)
    font_tick = fm.FontProperties(fname=times, size=9.5) if times else fm.FontProperties(size=9.5)

    steps, energies, forces, scf_corrections = parse_logs()
    print(f"[AutoGraph] Parsed {len(steps)} data points. Steps: {steps}")

    out_dirs = [os.getcwd()]
    backup_dir = get_backup_dir()
    if backup_dir and os.path.exists(backup_dir):
        out_dirs.append(backup_dir)
        print(f"[AutoGraph] Found backup dir: {backup_dir}")

    max_step = max(steps) if len(steps) > 0 else 1

    # 1. Total Energy progression
    for out_dir in out_dirs:
        fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
        ax.plot(steps, energies, color=color, linestyle='-', linewidth=1.2, zorder=3)
        ax.scatter(steps, energies, marker=marker, facecolors='none', edgecolors=color, s=msize, linewidths=1.2, zorder=4)
        ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
        ax.set_ylabel(r"系全体のエネルギー [$\mathrm{eV}$]", fontproperties=font_label, labelpad=2)
        ax.set_xlim(-0.5, max_step + 0.5)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
        ax.ticklabel_format(style='plain', axis='y')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(font_tick)
        plt.subplots_adjust(left=0.28, right=0.96, top=0.94, bottom=0.18)
        base = os.path.join(out_dir, "Total_Energy_progression")
        plt.savefig(f"{base}.png", dpi=dpi)
        plt.savefig(f"{base}.pdf")
        plt.savefig(f"{base}.svg")
        plt.close()

    # 2. Total Force progression
    if len(forces) > 0:
        for out_dir in out_dirs:
            fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
            ax.plot(steps[:len(forces)], forces, color=color, linestyle='-', linewidth=1.2, zorder=3)
            ax.scatter(steps[:len(forces)], forces, marker=marker, facecolors='none', edgecolors=color, s=msize, linewidths=1.2, zorder=4)
            ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
            ax.set_ylabel(r"Total force [$\mathrm{Ry/au}$]", fontproperties=font_label, labelpad=5)
            ax.set_xlim(-0.5, max_step + 0.5)
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontproperties(font_tick)
            plt.subplots_adjust(left=0.22, right=0.95, top=0.94, bottom=0.18)
            base = os.path.join(out_dir, "Total_Force_progression")
            plt.savefig(f"{base}.png", dpi=dpi)
            plt.savefig(f"{base}.pdf")
            plt.savefig(f"{base}.svg")
            plt.close()

    # 3. Total SCF Correction progression
    if len(scf_corrections) > 0:
        for out_dir in out_dirs:
            fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
            ax.plot(steps[:len(scf_corrections)], scf_corrections, color=color, linestyle='-', linewidth=1.2, zorder=3)
            ax.scatter(steps[:len(scf_corrections)], scf_corrections, marker=marker, facecolors='none', edgecolors=color, s=msize, linewidths=1.2, zorder=4)
            ax.set_xlabel("構造緩和ステップ数 [Step]", fontproperties=font_label, labelpad=5)
            ax.set_ylabel(r"Total SCF correction [$\mathrm{Ry/au}$]", fontproperties=font_label, labelpad=5)
            ax.set_xlim(-0.5, max_step + 0.5)
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontproperties(font_tick)
            plt.subplots_adjust(left=0.22, right=0.95, top=0.94, bottom=0.18)
            base = os.path.join(out_dir, "Total_SCF_Correction_progression")
            plt.savefig(f"{base}.png", dpi=dpi)
            plt.savefig(f"{base}.pdf")
            plt.savefig(f"{base}.svg")
            plt.close()

    print("[AutoGraph] Successfully generated all 3 progression graphs (PNG, PDF, SVG) in:")
    for d in out_dirs:
        print(f"  - {d}")


if __name__ == "__main__":
    main()

