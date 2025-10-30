#!/usr/bin/env python3

from ase.io import write
import click
import os
from mdkits.util import out_err, arg_type


@click.command(name='convert')
@click.argument('atoms', type=arg_type.Structure)
@click.option('-c', help='covert to cif', is_flag=True)
@click.option('-x', help='covert to xyz', is_flag=True)
@click.option('-d', help='covert to lammps data file', is_flag=True)
@click.option('-v', help='covert to vasp', is_flag=True)
@click.option('--coord', help='coord format', is_flag=True)
@click.option('--cp2k', help='convert to cp2k format(coord + cell)', is_flag=True)
@click.option('--center', help='center atoms', is_flag=True)
@click.option('--cell', type=arg_type.Cell, help='set cell, a list of lattice: --cell x,y,z or x,y,z,a,b,c')
def main(atoms, c, x, d, v, coord, cp2k, center, cell):
    """
    convet structure file in some formats
    """
    out_err.check_cell(atoms, cell)
    o = atoms.filename.split('.')[-2]


    if center:
        atoms.center()

    if c:
        o += '.cif'
        write(o, atoms, format='cif')

    if x:
        o += '.xyz'
        write(o, atoms, format='extxyz')

    if d:
        o += '.data'
        write(o, atoms, format='lammps-data', atom_style='atomic')

    if v:
        o = 'POSCAR'
        write(o, atoms, format='vasp')


    if cp2k:
        o = 'coord.xyz'
        write(o, atoms, format='xyz')
        with open(o, 'r') as f:
            lines = f.readlines()
        with open(o, 'w') as f:
            f.writelines(lines[2:])
        with open('cell.inc', 'w') as f:
            cell = atoms.cell.cellpar()
            f.write(f"ABC [angstrom] {cell[0]} {cell[1]} {cell[2]}\n")
            f.write(f"ALPHA_BETA_GAMMA {cell[3]} {cell[4]} {cell[5]}\n")


    out_err.path_output(o)


if __name__ == '__main__':
    main()
