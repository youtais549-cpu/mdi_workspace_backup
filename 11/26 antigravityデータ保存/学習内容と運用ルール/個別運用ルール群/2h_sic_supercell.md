# 2H-SiC Supercell Construction Rules

When assisting with the construction of 2H-SiC supercells or interpreting user requests regarding SiC layers, adhere to the following rules:

1. **Unit Cell Knowledge**: The basic 2H-SiC unit cell already contains **2 layers** of Si-C atom pairs (A and B stacking) along the c-axis.
2. **Expansion Factor Math**: Expanding the unit cell by a factor of `N` along the c-axis will result in `2 × N` layers total.
   - For example, a `3x3x2` supercell yields **4 layers** along the c-axis.
   - To achieve exactly 2 layers (the original thickness), the expansion factor must be `3x3x1`.
3. **User Clarification**: If a user requests a supercell dimensions like `3x3x2` while stating they want "2 layers," kindly correct their misunderstanding before proceeding.
4. **Tooling**: Use Python and the `ase` (Atomic Simulation Environment) library (`ase.build.make_supercell`) to construct these structures automatically.
5. **Output Formats**: When generating supercells, output both `.cif` (to preserve lattice information) and `.xyz` (for immediate visualization in tools like Winmostar).
