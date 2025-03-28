#!/usr/bin/env python3

from ase.io import write
from argparse import ArgumentParser
import os
from mdtool.util import encapsulated_ase


def parse_size(s):
    if s == None:
        return None
    return [float(x) for x in s.replace(',', ' ').split()]


def parse_argument():
    parser = ArgumentParser(description='covert structure file')
    parser.add_argument('file_name', type=str, help='input structure file name')
    parser.add_argument('-c', help='covert to cif', action='store_true')
    parser.add_argument('-x', help='covert to xyz', action='store_true')
    parser.add_argument('-d', help='covert to lammps data file', action='store_true')
    parser.add_argument('-v', help='covert to vasp', action='store_true')
    parser.add_argument('--coord', help='coord format', action='store_true')
    parser.add_argument('--center', help='center atoms', action='store_true')
    parser.add_argument('--cell', type=parse_size, help='set xyz file cell, --cell x,y,z,a,b,c')
    parser.add_argument('--cp2k', help='output cp2k format', action='store_true')
    parser.add_argument('-o', type=str, help='specify the output file name without suffix, default is "out"', default='out')

    return parser.parse_args()


def main():
    args = parse_argument()

    atoms = encapsulated_ase.atoms_read_with_cell(args.file_name, cell=args.cell, coord_mode=args.coord)

    if args.center:
        atoms.center()

    if args.c:
        args.o += '.cif'
        write(args.o, atoms, format='cif')

    if args.x:
        args.o += '.xyz'
        write(args.o, atoms, format='extxyz')

    if args.d:
        args.o += '.data'
        write(args.o, atoms, format='lammps-data', atom_style='atomic')

    if args.v:
        args.o = 'POSCAR'
        write(args.o, atoms, format='vasp')


    if args.cp2k:
        args.o = 'coord.xyz'
        write(args.o, atoms, format='xyz')
        with open(args.o, 'r') as f:
            lines = f.readlines()
        with open(args.o, 'w') as f:
            f.writelines(lines[2:])
        with open('cell.inc', 'w') as f:
            cell = atoms.cell.cellpar()
            f.write(f"ABC [angstrom] {cell[0]} {cell[1]} {cell[2]}\n")
            f.write(f"ALPHA_BETA_GAMMA {cell[3]} {cell[4]} {cell[5]}\n")


    print(os.path.abspath(args.o))


if __name__ == '__main__':
    main()
