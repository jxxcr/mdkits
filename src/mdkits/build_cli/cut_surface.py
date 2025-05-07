#!/usr/bin/env python3

from ase import build
import click, os
from mdkits.util import arg_type, out_err
from mdkits.build_cli import supercell


@click.command(name='cut')
@click.argument('atoms', type=arg_type.Structure)
@click.option('--face', type=click.Tuple([int, int, int]), help='face index')
@click.option('--size', type=click.Tuple([int, int, int]), help='surface size')
@click.option('--vacuum', type=float, help='designate vacuum of surface, default is None', default=0.0, show_default=True)
@click.option('--cell', type=arg_type.Cell, help='set xyz file cell, --cell x,y,z,a,b,c')
def main(atoms, face, vacuum, size, cell):
    """cut surface"""
    out_err.check_cell(atoms, cell)

    surface = build.surface(atoms, face, size[2], vacuum=vacuum/2)
    super_surface = supercell.supercell(surface, size[0], size[1], 1)

    o = f"{atoms.filename.split('.')[-2]}_{face[0]}{face[1]}{face[2]}_{size[0]}{size[1]}{size[2]}.cif"
    super_surface.write(o)
    print(os.path.abspath(o))


if __name__ == '__main__':
    main()
