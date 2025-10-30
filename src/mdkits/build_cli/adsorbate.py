#!/usr/bin/env python3

from ase import build
import os
import click
import numpy as np
import MDAnalysis
from mdkits.util import arg_type, encapsulated_ase, out_err


@click.command(name='adsorbate')
@click.argument('atoms', type=arg_type.Structure)
@click.argument('adsorbate', type=arg_type.Molecule)
@click.option('--cell', type=arg_type.Cell, help='set cell, a list of lattice: --cell x,y,z or x,y,z,a,b,c')
@click.option('--select', type=str, help="select adsorbate position")
@click.option('--height', type=float, help='height above the surface')
@click.option('--rotate', type=click.Tuple([float, float, float]), help='rotate adsorbate molcule around x, y, z axis', default=(0, 0, 0), show_default=True)
@click.option('--offset', type=click.Tuple([float, float]), help='adjust site', default=(0, 0), show_default=True)
@click.option("--cover", type=int, help='cover the surface with adsorbate randomly')
def main(atoms, adsorbate, cell, select, height, rotate, offset, cover):
    """add adsorbate molcule to the surface"""
    if height is None:
        raise ValueError("height is required")

    out_err.check_cell(atoms, cell)
    offset = np.array(offset)
    u = encapsulated_ase.atoms_to_u(atoms)

    molecule = build.molecule(adsorbate)
    molecule.rotate(rotate[0], 'x')
    molecule.rotate(rotate[1], 'y')
    molecule.rotate(rotate[2], 'z')

    output_filename = f"{atoms.filename.split('.')[0]}_{adsorbate}.cif"

    s = u.select_atoms(select)
    positions = s.positions[:, 0:2] + offset
    if cover:
        for index in np.random.choice(positions.shape[0], cover, replace=False):
            build.add_adsorbate(atoms, molecule, height, position=positions[index])
    else:
        for position in positions:
            build.add_adsorbate(atoms, molecule, height, position=position)


    atoms.write(output_filename, format='cif')

    out_err.path_output(output_filename)


if __name__ == '__main__':
    main()

