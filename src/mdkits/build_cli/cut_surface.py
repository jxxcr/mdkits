#!/usr/bin/env python3

from ase import build
import click, os
from mdkits.util import arg_type, out_err
from mdkits.build_cli import supercell
import numpy as np


@click.command(name='cut')
@click.argument('atoms', type=arg_type.Structure)
@click.option('--face', type=click.Tuple([int, int, int]), help='face index')
@click.option('--size', type=click.Tuple([int, int, int]), help='surface size')
@click.option('--vacuum', type=float, help='designate vacuum of surface, default is None', default=0.0, show_default=True)
@click.option('--cell', type=arg_type.Cell, help='set xyz file cell, --cell x,y,z,a,b,c')
@click.option('--orth', is_flag=True, help='orthogonalize cell')
def main(atoms, face, vacuum, size, cell, orth):
    """cut surface"""
    out_err.check_cell(atoms, cell)

    surface = build.surface(atoms, face, size[2], vacuum=vacuum/2)
    super_surface = supercell.supercell(surface, size[0], size[1], 1)

    if orth:
        super_surface_cell = super_surface.cell.cellpar()
        gamma = super_surface_cell[-1]
        if gamma != 90:
            b = np.sin(np.radians(gamma)) * super_surface_cell[1]
            super_surface_cell[1] = b
            super_surface_cell[-1] = 90
            super_surface.set_cell(super_surface_cell)

    o = f"{atoms.filename.split('.')[-2]}_{face[0]}{face[1]}{face[2]}_{size[0]}{size[1]}{size[2]}.cif"
    super_surface.write(o)
    out_err.cell_output(super_surface.cell.cellpar())
    out_err.path_output(o)


if __name__ == '__main__':
    main()
