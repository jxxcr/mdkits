#!/usr/bin/env python3

from ase import io, build
import argparse
from util import encapsulated_ase


def parse_size(s):
    return [int(x) for x in s.replace(',', ' ').split()]

def parse_size1(s):
    return [float(x) for x in s.replace(',', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description='cut surface of structure')
    parser.add_argument('filename', type=str, help='init structure filename')
    parser.add_argument('--face', type=parse_size, help='face index')
    parser.add_argument('--vacuum', type=float, help='designate vacuum of surface, default is None', default=0.0)
    parser.add_argument('--size', type=parse_size, help='surface size')
    parser.add_argument('--coord', help='coord format', action='store_true')
    parser.add_argument('--cell', type=parse_size1, help='set xyz file cell, --cell x,y,z,a,b,c')

    return parser.parse_args()


def main():
    args = parse_argument()
    atoms = encapsulated_ase.atoms_read_with_cell(args.filename, cell=args.cell, coord_mode=args.coord)
    surface = build.surface(atoms, args.face, args.size[2], vacuum=args.vacuum/2)
    super_cell = [[args.size[0], 0, 0], [0, args.size[1], 0], [0, 0, 1]]
    super_surface = build.make_supercell(surface, super_cell)

    super_surface.write(f"{args.filename.split('.')[-2].split('/')[-1]}_{args.face[0]}{args.face[1]}{args.face[2]}.cif")


if __name__ == '__main__':
    main()
