#!/usr/bin/env python3

import argparse
from ase.build import bulk
from ase.geometry import cell_to_cellpar
from ase.io import write


def parse_size(s):
    return [int(x) for x in s.replace(',', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description='build a surface structure of matel')
    parser.add_argument('symbol', type=str, help='designate the symbol of matel')
    parser.add_argument('--crystal', type=str, help='designate the crystal of structure')
    parser.add_argument('--orth', help='outpue orthorhombic crystal', action='store_true')
    parser.add_argument('-a', type=float, help='designate a lattice constant')
    parser.add_argument('--primitve', help='designate a lattice constant of real', action='store_true')
    parser.add_argument('-o', type=str, help='output structure name', default='bulk.xyz')
    parser.add_argument('-c', help='output coord.xyz and cell.inc', action='store_true')
    parser.add_argument('-k', help='output kpoint.inc', action='store_true')

    return parser.parse_args()


def main():
    args = parse_argument()
    if args.primitve:
        a = args.a * 0.7071 * 2
    else:
        a = args.a
    atoms = bulk(args.symbol, args.crystal, a=a, orthorhombic=args.orth)
    if args.c:
        atoms.write('coord.xyz', format='xyz')
        with open('coord.xyz', 'r') as f:
            lines = f.readlines()[2:]
        with open('coord.xyz', 'w') as f:
            f.writelines(lines)
        with open('cell.inc', 'w') as f:
            cell = list(cell_to_cellpar(atoms.cell))
            f.write('ABC [angstrom] ' + str(cell[0]) + ' ' + str(cell[1]) + ' ' + str(cell[2]) + ' ' + '\n')
            f.write('ALPHA_BETA_GAMMA ' + str(cell[3]) + ' ' + str(cell[4]) + ' ' + str(cell[5]) + '\n')
        if args.k:
            with open('kpoint.inc', 'w') as f:
                if True:
                    if True:
                        f.write(f"SCHEME MONKHORST-PACK {int(round(30/cell[0]))} {int(round(30/cell[1]))} {int(round(30/cell[2]))}" + "\n")
    else:
        atoms.write(args.o)


if __name__ == '__main__':
    main()

