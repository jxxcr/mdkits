from ase.io import write, read
import argparse
from ase.geometry import cell_to_cellpar, cellpar_to_cell
import math


def parse_argument():
    parser = argparse.ArgumentParser(description='combain solbox and surface to a interface')
    parser.add_argument('--surface', type=str, help='surface path')
    parser.add_argument('--sol', type=str, help='solbox path')
    parser.add_argument('--move', type=float, help='move at z, default = 0', default=0)
    parser.add_argument('--interval', type=float, help='interval between surface to sol, default is 2', default=2)
    parser.add_argument('--vacuum', type=float, help='vacuum of structure, default is 0', default=0)
    parser.add_argument('--symmetry', help='two side interface, default is false', action='store_true')
    parser.add_argument('--ne', help='two side interface, one side is Ne atom, default is false', action='store_true')
    parser.add_argument('-o', type=str, help='output file name', default='interface')

    return parser.parse_args()


def chformat(input_filename, output_filename, format):
    atoms = read(input_filename)
    write(output_filename, atoms, format=format)


def main():
    args = parse_argument()
    surface = read(args.surface)
    surface.set_pbc(True)
    surface.center()
    sy_surface = surface.copy()
    cell = surface.get_cell()
    [lenx, leny, lenz, anga, angb, angc] = cell_to_cellpar(cell)

    solbox = read(args.sol)
    solbox_cell = solbox.cell.cellpar()
    solbox.set_pbc(True)
    solbox.center()
    tmp_list = solbox.get_positions()
    tmp_list[:, 2] += lenz + args.interval
    solbox.set_positions(tmp_list)

    surface.extend(solbox)
    surface.cell = [lenx, leny, (lenz + args.interval + solbox_cell[2] + args.interval), anga, angb, angc]
    surface.center()

    if args.symmetry:
        tmp_list = surface.get_positions()
        tmp_list[:, 2] += -(lenz + args.interval + solbox_cell[2] + args.interval)
        surface.set_positions(tmp_list)
        surface.extend(sy_surface)
        surface.cell = [lenx, leny, (lenz + args.interval + solbox_cell[2] + args.interval + lenz + args.vacuum), anga, angb, angc]
        surface.center()
    elif args.ne:
        from ase import Atoms
        ne_interval = 4 # adjust water density
        ne_cell = [lenx, leny, 2, 90, 90, 90]
        ne_position = []
        ne_symbols = []
        ne_site = [int(lenx//ne_interval), int(leny//ne_interval)]
        for i in range(ne_site[0]):
            for j in range(ne_site[1]):
                ne_position.append((i*ne_interval, j*ne_interval, 0))
                ne_symbols.append('Ne')
        ne_atoms = Atoms(symbols=ne_symbols, positions=ne_position, cell=ne_cell)
        ne_atoms.center()
        tmp_list = surface.get_positions()
        tmp_list[:, 2] += -(lenz + args.interval + solbox_cell[2])
        surface.set_positions(tmp_list)
        surface.extend(ne_atoms)
        surface.cell = [lenx, leny, (lenz + args.interval + solbox_cell[2] + args.interval + 2 + args.vacuum), anga, angb, angc]
        surface.center()
    else:
        surface.set_pbc(True)
        tmp_list = surface.get_positions()
        #tmp_list[:, 2] -= lenz
        tmp_list[:, 2] -= args.move
        surface.set_positions(tmp_list)


    write(args.o + '.xyz', surface, format='extxyz')
    write(args.o + '.cif', surface, format='cif')
    #chformat(args.o + '.cif', args.o + '.xyz', format='xyz')

if __name__ == '__main__':
    main()
