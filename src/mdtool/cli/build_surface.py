#!/usr/bin/env python3

import argparse, sys
from ase import build
from ase.geometry import cell_to_cellpar
from ase.io import write
import numpy as np



def parse_size(s):
    if s == None:
        return None
    return [int(x) for x in s.replace(',', ' ').split()]


def surface_check(obj, surface_type):
    if hasattr(obj, surface_type):
        return getattr(obj, surface_type)
    else:
        print(f'dont have face named {surface_type}')
        exit()


def parse_argument():
    parser = argparse.ArgumentParser(description='build a surface structure of matel')
    parser.add_argument('symbol', type=str, help='designate the symbol of matel')
    parser.add_argument('--face', type=str, help='designate the face of surface')
    parser.add_argument('-a', type=float, help='designate a lattice constant', default=None)
    parser.add_argument('--primitive', help='designate a lattice constant of real', action='store_true')
    parser.add_argument('--size', type=parse_size, help='designate surface size(a,b,c)')
    parser.add_argument('--vacuum', type=float, help='designate vacuum of surface, default is None', default=0.0)
    parser.add_argument('--adsorbate', type=str, help='add adsorbate on surface', default=None)
    parser.add_argument('--position', type=str, help='position of adsorbate', default='ontop')
    parser.add_argument('--offset', type=str, help='offset')
    parser.add_argument('--height', type=float, help='position of adsorbate', default=1)
    parser.add_argument('-o', type=str, help='output structure name', default='surface.xyz')
    parser.add_argument('-c', help='output coord.xyz and cell.inc', action='store_true')
    parser.add_argument('-k', type=parse_size, help='output kpoint.inc(a,b,c)', default=None)
    parser.add_argument('--autok',  help='output kpoint.inc', action='store_true')
    parser.add_argument('--orth',  help='orth cell', action='store_true')
    parser.add_argument('--coverh',  type=int, help='cover H atom', default=0)

    return parser.parse_args()


def main():
    args = parse_argument()
    if args.primitive:
        a = args.a * 0.7071 * 2
    else:
        a = args.a

    vacuum = args.vacuum / 2

    build_surface = surface_check(build, args.face)

    if args.orth:
        atoms = build_surface(args.symbol, args.size, a=a, vacuum=vacuum, orthogonal=args.orth)
    else:
        atoms = build_surface(args.symbol, args.size, a=a, vacuum=vacuum)

    # add adsorbate
    if args.adsorbate != None:
        ## add H2Oa and OH
        if args.adsorbate in ['H2Oa', 'OH']:
            if args.adsorbate in ['OH']:
                h2o = build.molecule(args.adsorbate)
                h2o.rotate(90, 'y')
                build.add_adsorbate(atoms, h2o, args.height, position=args.position, offset=args.offset)
            else:
                h2o = build.molecule('H2O')
                h2o.rotate(90, 'y')
                build.add_adsorbate(atoms, h2o, args.height, position=args.position, offset=args.offset)
        ## add H2Ob
        elif args.adsorbate in  ['H2Ob']:
            h2o = build.molecule('H2O')
            h2o.rotate(90, 'z')
            h2o.rotate(45, 'y')
            build.add_adsorbate(atoms, h2o, args.height, position=args.position, offset=args.offset)
        ## add default something
        else:
            build.add_adsorbate(atoms, args.adsorbate, args.height, position=args.position, offset=args.offset)

    # add h with coverage
    if args.coverh != 0:
        ## get atom position at surface
        surface_positions_dict = {}
        for atom in atoms:
            if atom.tag == 1:
                surface_positions_dict[atom.index] = atom.position
        ## error checking
        if site_number := len(surface_positions_dict) < args.coverh:
            print(f"coverh is too big, please less then {site_number}")
            sys.exit()
        ## get random site
        random_site_list = np.random.choice(list(surface_positions_dict.keys()), args.coverh, replace=False)
        random_site_list = np.unique(random_site_list)
        ## add H atom at hollow site
        for site in random_site_list:
            site_position = surface_positions_dict[site][0:2]
            build.add_adsorbate(atoms, 'H', 2, position=site_position, offset=(0.3, 0.3))

    # control output format
    ## output with coord.xyz(cp2k format)
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
            ## output kpoint file with specific number
            if args.k != None:
                if True: #judge M or G
                    with open('kpoint.inc', 'w') as f:
                        f.write(f"SCHEME MONKHORST-PACK {args.k[0]} {args.k[1]} {args.k[2]}" + "\n")
            ## output kpoint file autoly
            if args.autok:
                if True: # judge matel or semi or else
                    if True: # judge M or G
                        with open('kpoint.inc', 'w') as f:
                            f.write(f"SCHEME MONKHORST-PACK {int(round(30/cell[0]))} {int(round(30/cell[1]))} {int(round(30/cell[2]))}" + "\n")
    ## output default format or specific xyz file
    else:
        atoms.write(args.o)


if __name__ == '__main__':
    main()

