#!/usr/bin/env python3

from ase.io import read
import click, os
import numpy as np
from ase.build import make_supercell
from mdkits.util import (
    structure_parsing,
    encapsulated_ase,
    cp2k_input_parsing,
    arg_type,
    out_err,
    )


def supercell(atom, x, y, z):
    P = [ [x, 0, 0], [0, y, 0], [0, 0, z] ]
    super_atom = make_supercell(atom, P)
    return super_atom


@click.command(name='supercell')
@click.argument('atoms', type=arg_type.Structure)
@click.argument('super', type=click.Tuple([int, int, int]), default=(1, 1, 1))
@click.option('--cell', type=arg_type.Cell, help='set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c')
def main(atoms, super, cell):
    """make a supercell"""

    out_err.check_cell(atoms, cell)

    atoms.set_pbc(True)
    atoms.wrap()
    super_atom = supercell(atoms, super[0], super[1], super[2])

    o = f"{atoms.filename.split('.')[-2]}_{super[0]}{super[1]}{super[2]}.cif"
    super_atom.write(o)
    out_err.path_output(o)


if __name__ == '__main__':
    main()
