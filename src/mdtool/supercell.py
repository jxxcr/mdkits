#!/usr/bin/env python3

from ase.io import read
import argparse, os
import numpy as np
from ase.build import make_supercell
from util import (
    structure_parsing,
    encapsulated_ase,
    cp2k_input_parsing
    )


def supercell(atom, x, y, z):
    P = [ [x, 0, 0], [0, y, 0], [0, 0, z] ]
    super_atom = make_supercell(atom, P)
    return super_atom


def parse_cell(s):
    return [float(x) for x in s.replace(',', ' ').split()]


def super_cell(s):
    super_cell = [int(x) for x in s.replace(',', ' ').split()]
    leng = len(super_cell)
    if leng == 2:
        super_cell.append(1)
    elif leng == 3:
        pass
    else:
        print('wrong super cell size')
        exit(1)

    return super_cell


def parse_argument():
    parser = argparse.ArgumentParser(description='make a supercell')

    parser.add_argument('input_file_name', type=str, help='input file name')
    parser.add_argument('super', type=super_cell, help='super cell size, a,b,c')
    parser.add_argument('-o', type=str, help='output file name, default is "super.cif"', default='super.cif')
    parser.add_argument('--cp2k_input_file', type=str, help='input file name of cp2k, default is "input.inp"', default='input.inp')
    parser.add_argument('--coord', help='coord format', action='store_true')
    parser.add_argument('--cell', type=parse_cell, help='set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c')

    return parser.parse_args()


def main():
    args = parse_argument()
    if args.input_file_name == None:
        print('give a xyz file')
        sys.exit()

    atom = encapsulated_ase.atoms_read_with_cell(args.input_file_name, cell=args.cell, coord_mode=args.coord)
    atom.set_pbc(True)
    atom.wrap()
    super_atom = supercell(atom, args.super[0], args.super[1], args.super[2])

    suffix = args.o.split('.')[-1]
    if suffix == 'data':
        super_atom.write(f'{args.o}', format='lammps-data', atom_style='atomic')
    else:
        super_atom.write(f'{args.o}')

    print(os.path.abspath(args.o))


if __name__ == '__main__':
    main()
