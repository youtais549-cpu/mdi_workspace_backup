from ase.io import read, write
atoms = read('2H-SiC_supercell_3x3x2.cif')
write('2H-SiC_supercell_3x3x2.data', atoms, format='lammps-data')
