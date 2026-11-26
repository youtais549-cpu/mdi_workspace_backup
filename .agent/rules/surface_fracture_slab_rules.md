# Surface Fracture Energy & 2H-SiC Slab Model Standards

When assisting with model generation, theoretical explanation, or validation of surface fracture energy calculations for 2H-SiC, adhere strictly to these principles:

## 1. Surface Fracture Energy Definition
- **Formula**:
  $$\gamma = \frac{\Delta E}{2A} = \frac{E_{\text{slab}}(N) - E_{\text{bulk}}(N)}{2A}$$
- **Equal Number of Atoms ($N$)**: The slab model ($E_{\text{slab}}$) and the bulk reference model ($E_{\text{bulk}}$) MUST have the exact same number of atoms and stoichiometry ("same size cake").
- **Denominator $2A$**: Cleaving along 1 plane of cross-sectional area $A$ creates **two** surfaces (top and bottom), resulting in a total newly created surface area of $2A$.
- **Physical Meaning of $\Delta E$**: $\Delta E$ represents the chemical bond breaking energy PLUS the surface structural relaxation energy (reconstruction / strain release of under-coordinated surface atoms). It is NOT the intrinsic energy of the surface atoms alone.

## 2. Material & Crystal Plane Selection
- **Material: 2H-SiC (Wurtzite)**
  - *Primary reason*: Smallest periodic stacking repeat along the c-axis (1 repeat = 2 layers), minimizing unit cell dimensions and DFT/MD computational cost.
  - *Secondary reason*: Inomata & Inoue (1970) establishes 2H-SiC as a stable phase below 1400°C (including room temperature ~30°C).
- **Crystal Plane: $\{10\bar{1}0\}$ Prismatic Plane (m-plane)**
  - *Non-polar Surface*: Stoichiometric 1:1 ratio of Si and C in every layer. Net dipole moment along $z$ is strictly zero (Tasker Type I), preventing artificial electrostatic divergence in the vacuum layer (unlike polar $(0001)$ basal planes).
  - *Minimal Complexity*: Avoids complex tilted pyramidal planes (e.g., $\{10\bar{1}1\}$ or $\{11\bar{2}2\}$), having minimal unit cell area ($a \times c$) compared to $\{11\bar{2}0\}$ (which requires $\sqrt{3}a \times c$).
  - *Benchmark Data*: Allows direct validation against Rauls et al., Solid State Commun. 111, 459 (1999).

## 3. Slab Construction Specifications
- **Bilayer & Cleavage Termination（自然へき開面の物理的前提・粗結合切断の絶対厳守）**:
  - The $\{10\bar{1}0\}$ m-plane has alternating layer spacings: dense bond layers ($dz \approx 0.888\text{ \AA}$, 4 bonds/cell, strong Si-C dimer pairs) and sparse bond layers ($dz \approx 1.776\text{ \AA}$, 2 bonds/cell, weak cleavage planes).
  - **き裂進展・脆性破壊シミュレーションの根本前提**: き裂は必ずエネルギー最小となる「最も結合が疎で弱い自然へき開面（Cleavage Plane）」を進む。
  - **スラブ切断面（真空層境界）は、必ず「$1.776\text{ \AA}$ の粗結合面」でなければならない**。
  - 最外層の密結合ペア（$0.888\text{ \AA}$）を引きちぎるような切断位置でモデルを作成することは**物理的前提が破綻するため絶対禁止**。
  - To ensure both top and bottom fracture surfaces are **crystallographically and energetically equivalent** ($\gamma_{\text{top}} = \gamma_{\text{bottom}}$), the slab must be cut in integer multiples of 2 layers (1 repeat = 2 layers).
  - Both top and bottom terminations MUST be exposed at the sparse bond cleavage planes ($dz \approx 1.776\text{ \AA}$) and maintain equal stoichiometry of Si and C (non-polar Tasker Type I surface).
- **Vacuum Layer**:
  - Insert vacuum of at least 10.0 Å above the top layer and 10.0 Å below the bottom layer (total vacuum $\ge 20.0\text{ \AA}$) to eliminate spurious interactions between periodic slab replicas along $z$.
- **Boundary Conditions**:
  - 3D Periodic Boundary Conditions (PBC = [True, True, True]) using an Orthorhombic cell ($\alpha=\beta=\gamma=90^\circ$).

## 4. Surface Area Evaluation & Unit Conversion
- **Cross-Sectional Area $A$**:
  - $A = L_x \times L_y$ (where $z$ is the cleavage normal).
  - For $3\times 3\times 2$ $\{10\bar{1}0\}$ model: $L_x = 9.2280\text{ \AA}$, $L_y = 15.1440\text{ \AA} \implies A = 139.7488\text{ \AA}^2$.
  - Total newly created surface area: $2A = 279.4977\text{ \AA}^2$.
- **Unit Conversion Factor**:
  - $1\text{ eV/\AA}^2 = \frac{1.6021766 \times 10^{-19}\text{ J}}{1.0 \times 10^{-20}\text{ m}^2} \approx 16.021766\text{ J/m}^2$.
  - Practical formula:
    $$\gamma [\text{J/m}^2] = \frac{E_{\text{slab}} [\text{eV}] - E_{\text{bulk}} [\text{eV}]}{2A [\text{\AA}^2]} \times 16.021766 \approx \frac{\Delta E}{17.4449}$$
- **Literature Benchmark Value (Rauls et al., 1999 p.462 Fig.2)**:
  - Surface energy for Si-C dimer reconstructed $\{10\bar{1}0\}$ surface: $188\text{ meV/\AA}^2 = \mathbf{3.03\text{ J/m}^2}$.
  - Reference benchmark for non-polar $\{10\bar{1}0\}$ cleavage surface energy is strictly set to **$3.03\text{ J/m}^2$**.

## 5. Calculation Protocols: Static 0 K Relaxation vs. Finite-Temperature AIMD
- **Static 0 K Energy Minimization (`minimize`)**:
  - **Purpose**: Strict evaluation of surface fracture energy $\gamma = \frac{\Delta E}{2A}$ under defined ground-state conditions ($T = 0\text{ K}$).
  - **Literature Benchmark Parity**: Rauls et al. (1999) used 0 K geometry relaxation (DFTB/DFT-LDA) to obtain $\gamma_{\text{unrelaxed}} \approx 2.44\text{ J/m}^2$ and $\gamma_{\text{relaxed}} \approx 2.27\text{ J/m}^2$. Our MDI (LAMMPS + QE GPU) 0 K CG relaxation directly benchmarks against these values.
  - **Bulk Reference**: Evaluated via static single-point SCF calculation (`calculation = 'scf'`) at 0 K with Quantum ESPRESSO (`pw.x`).
  - **Strict DFT Parameter Parity**: All DFT settings (`ecutwfc = 40 Ry`, `ecutrho = 320 Ry`, $\Gamma$-point, pseudopotentials, smearing) MUST match exactly.
- **Finite-Temperature AIMD (300 K NVT)**:
  - **Purpose**: Investigation of thermal stability of reconstructed surface phases, thermal expansion, dynamic phonon vibrations, and future dynamic crack propagation.
  - **Decoupling from $\gamma$ Definition**: Thermal MD includes kinetic energy fluctuations ($E_{\text{kin}} = \frac{3}{2}Nk_BT$) and entropy ($F = E - TS$), so it is treated as a separate post-relaxation phase.

## 6. Automated Results Ledger & Post-Calculation Workflow
- **Master Ledger Maintenance**:
  - All calculated surface energy results MUST be permanently registered in `SURFACE_ENERGY_RESULTS.md` and `surface_energy_results.csv`.
- **Zero-Manual Post-Processing**:
  - Upon completion of any slab structural relaxation or bulk SCF calculation, the agent MUST automatically invoke:
    ```bash
    python3 modular_aimd_framework/parameters_variable/calc_surface_energy.py --auto \
      --slab-dir <SLAB_DIR> --bulk-dir <BULK_DIR>
    ```
  - This extracts $E_{\text{slab}}$, $E_{\text{bulk}}$, calculates $\Delta E$ and $\gamma$, updates both Markdown/CSV ledgers, and mirrors the results to Google Drive (`G:\マイドライブ\MD_backup\`).

## 7. 300 K NVT Ab Initio Molecular Dynamics (AIMD) Standards
When configuring finite-temperature AIMD for 2H-SiC slabs:
1. **Initial Structure**:
   - MUST use the **0 K fully relaxed structure** (`slab_10-10_relaxed.data`) to prevent unphysical bond breaking and SCF divergence caused by unrelaxed forces ($F_{\max} \approx 2.55\text{ eV/\AA}$).
2. **Time Step (`timestep`)**:
   - Set to `0.001 ps` ($1.0\text{ fs}$). This safely resolves the fastest optical phonon vibration of 2H-SiC ($\sim 33\text{ fs}$, ratio $> 1/30$).
3. **Thermostat (`fix nvt`)**:
   - Nosé-Hoover thermostat with damping time $T_{\text{damp}} = 0.1\text{ ps}$ ($100\text{ fs} = 100 \times \Delta t$, standard LAMMPS ratio).
4. **Center-of-Mass Drift Prevention (`fix momentum`)**:
   - For slab geometries with vacuum, MUST include `fix 3 all momentum 50 linear 1 1 1` to prevent rigid-body drift across PBC boundaries.
5. **Standard Simulation Horizon**:
   - Default: $1,000\text{ steps}$ ($1.0\text{ ps}$).
     - Steps 1–500 ($0.5\text{ ps}$): Thermal equilibration (temperature stabilizes at 300 K).
     - Steps 501–1,000 ($0.5\text{ ps}$): Thermal trajectory sampling (MSD, average surface configuration).
   - Execution time: $\approx 5.5\text{ hours}$ on Tesla T4 GPU (safe within single Colab session).

## 8. Vacuum Layer Thickness & Interaction Cutoff Threshold
- **Benchmark Findings (2H-SiC $\{10\bar{1}0\}$ Slab)**:
  - **10.0 Å (total vacuum 20.0 Å)**: $E_{\text{slab}} = -31,892.6375\text{ eV} \implies \gamma = 2.4488\text{ J/m}^2$.
  - **5.0 Å (total vacuum 10.0 Å)**: $E_{\text{slab}} = -31,892.6430\text{ eV} \implies \gamma = 2.4485\text{ J/m}^2$ ($\Delta \gamma = 0.0003\text{ J/m}^2$, 完全遮断).
  - **2.5 Å (total vacuum 5.0 Å)**: $E_{\text{slab}} = -31,892.2630\text{ eV} \implies \gamma = 2.4703\text{ J/m}^2$ ($\Delta \gamma \approx +0.0218\text{ J/m}^2$, 表面間相互作用を検知).
- **Critical Cutoff Guideline**:
  - 2H-SiC $\{10\bar{1}0\}$ における相互作用遮断の臨界真空層厚さは **$2.5\text{ \AA} \sim 5.0\text{ \AA}$**（片側厚さ）である。5.0 Å 以上あれば計算コストを抑えつつ十分な遮断精度が得られる。

## 9. Convergence Diagnostic & Early Termination Protocol for Slab CG Relaxation
- **Flat Potential Energy Surface & DFT Noise Floor**:
  - 真空層が極薄（2.5 Å等）の場合、対向スラブの電子雲干渉によりエネルギー面の底が極めて平坦になり、CG 法のラインサーチが微小歩幅探索を過剰に繰り返す。
  - Quantum ESPRESSO の SCF 収束閾値（`conv_thr = 1.0e-5 Ry`）に伴い、原子に働く力の数値ノイズ限界（フロア）は $\sim 0.0002\text{ Ry/au}$（$\approx 0.006\text{ eV/\AA}$）程度となる。
  - LAMMPS の収束閾値が `ftol = 1.0e-3 eV/Å`（0.0010 eV/Å）の場合、DFT のノイズ限界を「未収束」と誤認して最大イテレーションまで無駄に回り続ける現象が発生する。
- **Diagnostic & Early Termination Criteria**:
  - ① スラブ全エネルギーが直近複数ステップで小数第 4 位（$0.1\text{ meV}$ レベル）まで一定。
  - ② `dump.lammpstrj` の原子最大移動量が $\Delta r_{\max} \le 10^{-6}\text{ \AA}$（完全静止）。
  - ③ `espresso.pwo` の Total force が $\approx 0.0002\text{ Ry/au}$ 付近で停滞。
  - **上記 3 条件を満たした場合、構造緩和は $100\%$ 完了していると判定し、GPU 時間の浪費を防ぐため直ちに計算を正常終了・確定（Fix）させて成果物抽出へ移行すること。**

## 10. Publication-Quality Plotting Standards
When generating comparison graphs for surface fracture energy vs. vacuum thickness (see `GRAPH_STYLE_SPEC.md`):
1. **Aspect Ratio & Figure Size**: Rectangular (5.6 × 4.4 inches, dpi=300).
2. **Axis Labels**:
   - Y-axis: `表面破壊エネルギー [$\mathrm{J/m^2}$]` (14.5 pt, Units in Times New Roman).
   - X-axis: `真空層の厚さ [$\mathrm{\AA}$]` (14.5 pt, Units in Times New Roman).
3. **Axis Range & Tick Step**:
   - **Y-axis Range**: **$2.4 \sim 3.2\text{ J/m}^2$**（微小なエネルギー変化 $\Delta \gamma \approx 0.02\text{ J/m}^2$ を明確に識別可能にするため絞り込み）。
   - **Y-axis Ticks**: **`2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2` (0.1 刻み)**（Times New Roman 11.5 pt, 内向き目盛り線 `direction='in'`）。
   - **X-axis Range**: $0.0 \sim 16.0\text{ \AA}$。
   - **X-axis Ticks**: `0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0` (2.0 刻み)。
4. **Data Plotting**: Open purple triangles (`marker='^'`, `facecolors='none'`, color `#8A2BE2`, `s=70`, `linewidths=1.6`), points only (NO connecting lines).
5. **Literature Reference Line**:
   - Horizontal dashed line at $3.03\text{ J/m}^2$ (`ls='--'`, `lw=1.2`, color `#222222`).
   - Label: Bold Japanese `文献値` (12 pt) + Times New Roman Bold `(3.03 J/m²)` (12.5 pt), positioned neatly above the reference line.
6. **Font Fallback**: `Times New Roman` for English/numbers/math, `MS Gothic` / `Noto Sans CJK JP` for Japanese.

### Period Dependency Graph Standards (e.g. `周期数と表面破壊エネルギーの関係.*`):
- **X-axis**: `周期数 [periods]` (Range: 1 ~ 7, Ticks: `2, 4, 6`).
- **Y-axis**: `表面破壊エネルギー [$\mathrm{J/m^2}$]` (Range: **$2.2 \sim 3.2\text{ J/m}^2$**, Ticks: 0.1 step: `2.2, 2.3, 2.4, ... 3.2`).
- **Marker**: Open purple triangles (`marker='^'`, `facecolors='none'`, color `#8A2BE2`, `s=70`, `linewidths=1.6`), points only.
- **Reference line**: Horizontal dashed line at $3.03\text{ J/m}^2$ (`ls='--'`, `lw=1.2`, color `#222222`), Label: Bold Japanese `文献値` + Times New Roman Bold `(3.03 J/m²)`.
- **Data Integrity & Traceability**: MUST plot only objective raw calculated values extracted directly from `espresso.pwo` and `log.lammps` of each calculation. Never fabricate, adjust, or alter data to fit literature values.

## 11. Mandatory Progression Graph Suite for Relaxation Calculations
Whenever a slab relaxation calculation finishes (either by reaching convergence or via early termination protocol), the agent MUST automatically generate and store the following 3 progression plots in both the local results folder and Google Drive (`G:\マイドライブ\MD_backup\<MODEL_DIR>\`):
1. **Total Energy vs. Step (`Total_Energy_progression.*`)**:
   - Y-axis: `系全体のエネルギー [$\mathrm{eV}$]`
   - X-axis: `構造緩和ステップ数 [Step]`
2. **Total Force vs. Step (`Total_Force_progression.*`)**:
   - Y-axis: `Total force [$\mathrm{Ry/au}$]`
   - X-axis: `構造緩和ステップ数 [Step]`
3. **Total SCF Correction vs. Step (`Total_SCF_Correction_progression.*`)**:
   - Y-axis: `Total SCF correction [$\mathrm{Ry/au}$]`
   - X-axis: `構造緩和ステップ数 [Step]`

**Style Specifications**:
- Dimensions: 8.0 cm (width) × 6.2 cm (height) (optimized for Word two-column layout, 600 dpi).
- Fonts: MS Mincho (10.5 pt) for Japanese labels, Times New Roman (9.5 pt) for ticks/numbers, STIX for math.
- Markers: Open purple triangles (`marker='^'`, `facecolors='none'`, `edgecolors='#8A2BE2'`, `s=45`, `linewidths=1.2`) connected with line (`#8A2BE2`, `lw=1.2`).
- Frame & Ticks: 4-sided box (`top=True, right=True`), inward ticks (`direction='in'`).
- Reference line: NO literature reference line needed for progression plots.
## 12. Optimized Convergence Threshold Standards for All Slabs & File Preservation Principle
- **Optimized Convergence Criteria (`in.lammps.optimized_conv`)**:
  - Across all slab sizes (2 periods / 72 atoms, 4 periods / 144 atoms, 6 periods / 216 atoms, and beyond), Hellmann-Feynman forces exhibit a numerical noise floor of $\sim 0.0002 \sim 0.0003\text{ Ry/au}$ ($\approx 0.0051 \sim 0.0077\text{ eV/\AA}$) under QE `conv_thr = 1.0e-5 Ry`.
  - The universal standardized relaxation command is:
    ```lammps
    minimize 1.0e-6 1.0e-2 100 150
    ```
    - `ftol = 1.0e-2 eV/Å` ($= 0.010\text{ eV/\AA} \approx 0.0004\text{ Ry/au}$): Triggers natural termination once physical relaxation is complete.
    - `etol = 1.0e-6`: Dual safety net on relative energy stagnation ($\Delta E \le 0.06\text{ eV}$).
    - `maxiter = 100, maxeval = 150`: Upper bounds.
  - **Empirical Validation**:
    - For 2-period vac 2.5 Å (72 atoms), previously stuck under `ftol = 1.0e-3 eV/Å`, this setting achieved complete natural convergence in 31 min 43 sec. Surface fracture energy matched with an error of only 0.02% ($\gamma = 2.4709\text{ J/m}^2$ vs $2.4703\text{ J/m}^2$, $\Delta \gamma = +0.0006\text{ J/m}^2$).
- **Strict Non-Overwriting Principle**:
  - Whenever parameters (periods, vacuum thickness, convergence criteria) are altered, the agent MUST NOT overwrite existing files.
  - Create a new dedicated local directory (e.g. `calc_2H-SiC_10-10_<N>periods_vac<X>A/`) and Google Drive folder (`G:\マイドライブ\MD_backup\[101_0]<N>周期<X>Å\`).
  - Preserve `in.lammps.optimized_conv` alongside `in.lammps` for traceability.

## 13. 周期数拡張における ASE surface 厳格統一と切断面自動検証プロトコル
- **モデル生成ロジックの統一**:
  - 周期数を拡張（2周期 $\to$ 4周期 $\to$ 6周期）する際は、独自の手動座標生成スクリプトを持ち込むことを禁止し、2周期基準モデルと完全に同一の ASE ロジックで統一生成すること：
    ```python
    slab_unit = surface(bulk, indices=(1, 0, 0), layers=2 * n_periods, vacuum=None)
    slab = slab_unit * (supercell_x, supercell_y, 1)
    ```
- **生成後の必須層間間隔検証**:
  - スラブ生成後、計算投入前に必ず Z 座標のユニーク値から層間間隔プロファイルを検査すること：
    - 正しいプロファイル: `[0.888, 1.776, 0.888, ..., 0.888]`（両端が 0.888 Å で、外側が 1.776 Å 粗結合切断）
    - 誤ったプロファイル: `[1.776, 0.888, ..., 1.776]`（両端が 1.776 Å で、外側が 0.888 Å 強結合切断）$\implies$ **即時破棄・再生成**。
- **異常値の早期検知プロトコル**:
  - 表面破壊エネルギー $\gamma$ が文献値（$\approx 2.45\text{ J/m}^2$）から大きく乖離（数倍など）した場合、「スラブ厚み依存性」や「オーダーが合っている」などと安易に正当化してはならない。切断面の終端原子・結合状態を最優先で疑い検証すること。
