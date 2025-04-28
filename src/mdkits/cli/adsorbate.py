#!/usr/bin/env python3

from ase import io, build
from ase.collections import g2
import argparse, os
import numpy as np
from util import encapsulated_ase


def parse_size(s):
    if s == None:
        return None
    return [float(x) for x in s.replace(',', ' ').split()]


def parse_index(s):
    return [int(x)-1 for x in s.replace(',', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description='add some adsorbate')
    parser.add_argument('filename', type=str, help='init structure filename')
    parser.add_argument('-m', type=str, help='atom or molecule to add')
    parser.add_argument('--index', type=parse_index, help='index(list) of atom to add atom(top site)')
    parser.add_argument('--offset', type=parse_size, help='adjust site, default is 0,0', default='0,0')
    parser.add_argument('--height', type=float, help='designate vacuum of surface, default is None', default=0.0)
    parser.add_argument('-x', type=float, help='rotate axis and angle')
    parser.add_argument('-y', type=float, help='rotate axis and angle')
    parser.add_argument('-z', type=float, help='rotate axis and angle')
    parser.add_argument('-o', type=str, help='specify the output file name without suffix, default is "adsorbated.cif"', default='adsorbated.cif')
    parser.add_argument('--coord', help='coord format', action='store_true')
    parser.add_argument('--cell', type=parse_size, help='set xyz file cell, --cell x,y,z,a,b,c')
    parser.add_argument('--cp2k', help='output cp2k format', action='store_true')

    return parser.parse_args()

@click.option('--adsorbate', type=arg_type.Molecule, help='add adsorbate on surface')
@click.option('--site', type=click.Choice(['ontop', 'hollow','fcc', 'hcp', 'bridge', 'shortbridge', 'longbridge']))
@click.option('--height', type=float, help='height above the surface')
@click.option('--rotate', type=click.Tuple([float, float, float]), help='rotate adsorbate molcule around x, y, z axis', default=(0, 0, 0))
def main():
    args = parse_argument()
    atoms = encapsulated_ase.atoms_read_with_cell(args.filename, cell=args.cell, coord_mode=args.coord)

    if len(args.offset) < 2:
        args.offset.append(0)
    offset = np.array(args.offset)

    position_list = []
    for atom in atoms:
        if atom.index in args.index:
            position_list.append(np.copy(atom.position[0:2])+offset)

        molecule = build.molecule(adsorbate)
        molecule.rotate(rotate[0], 'x')
        molecule.rotate(rotate[1], 'y')
        molecule.rotate(rotate[2], 'z')
        build.add_adsorbate(atoms, molecule, position=site, height=height)
    if args.m in g2.names:
        molecule = build.molecule(args.m)
        if args.x:
            molecule.rotate(args.x, 'x')
        if args.y:
            molecule.rotate(args.y, 'y')
        if args.z:
            molecule.rotate(args.z, 'z')
        for position in position_list:
            build.add_adsorbate(atoms, molecule, args.height, position=position)
    else:
        for position in position_list:
            build.add_adsorbate(atoms, args.m, args.height, position=position)


    if args.cp2k:
        args.o = 'coord.xyz'
        atoms.write(args.o, format='xyz')
        with open(args.o, 'r') as f:
            lines = f.readlines()
        with open(args.o, 'w') as f:
            f.writelines(lines[2:])
        with open('cell.inc', 'w') as f:
            cell = atoms.get_cell().cellpar()
            f.write('ABC [angstrom] ' + str(cell[0]) + ' ' + str(cell[1]) + ' ' + str(cell[2]) + ' ' + '\n')
            f.write('ALPHA_BETA_GAMMA ' + str(cell[3]) + ' ' + str(cell[4]) + ' ' + str(cell[5]) + '\n')
    else:
        atoms.write(args.o, format='cif')

    print(os.path.abspath(args.o))


if __name__ == '__main__':
    main()

