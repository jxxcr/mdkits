#!/usr/bin/env python3

import argparse
from MDAnalysis import Universe
import MDAnalysis
import os
from util import (
    structure_parsing,
    encapsulated_ase,
    os_operation,
    cp2k_input_parsing
    )


def parse_cell(s):
    return [float(x) for x in s.replace(',', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description='wrap structure file')

    parser.add_argument('input_file_name', type=str, nargs='?', help='input file name', default=os_operation.default_file_name('*-pos-1.xyz', last=True))
    parser.add_argument('-o', type=str, help='output file name, default is "wraped.xyz"', default='wraped.xyz')
    parser.add_argument('--cp2k_input_file', type=str, help='input file name of cp2k, default is "input.inp"', default='input.inp')
    parser.add_argument('--process', type=int, help='paralle process number default is 28', default=30)
    parser.add_argument('--temp', help='keep temp file', action='store_false')
    parser.add_argument('--cell', type=parse_cell, help='set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c')
    parser.add_argument('--one',  help='only one structure', action="store_true")
    parser.add_argument('--big',  help='supercell 3X3X1', action="store_true")

    return parser.parse_args()

def main():
    args = parse_argument()
    if args.input_file_name == None:
        print('give a xyz file')
        sys.exit()


    cell = cp2k_input_parsing.get_cell(args.cp2k_input_file, args.cell)
    u = Universe(args.input_file_name)
    u.dimensions = cell
    ag = u.select_atoms("all")


    with MDAnalysis.Writer(args.o, ag.n_atoms) as W:
        for ts in u.trajectory:
            ag.wrap()
            W.write(ag)


    print(os.path.abspath(args.o))


if __name__ == '__main__':
    main()
