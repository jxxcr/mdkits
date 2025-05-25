#!/usr/bin/env python3

from ase import build
import click, os
from mdkits.util import arg_type, out_err
from mdkits.build_cli import supercell
import numpy as np
import ase.visualize


def find_vector(atoms):
    position = atoms.positions
    max_z = np.max(position[:, 2])
    highest_points = position[position[:, 2] == max_z]

    shortest_vector = None
    min_distance = float('inf')
    x_axis = np.array([1, 0, 0])

    for i in range(len(highest_points)):
        for j in range(i + 1, len(highest_points)):
            point1 = highest_points[i]
            point2 = highest_points[j]
            vector = point2 - point1

            cos_angle = np.dot(vector, x_axis) / (np.linalg.norm(vector) * np.linalg.norm(x_axis))
            angle = np.arccos(cos_angle)

            if angle <= np.pi / 2:
                distance = np.linalg.norm(vector)
                if distance < min_distance:
                    min_distance = distance
                    shortest_vector = vector

    return shortest_vector


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
    o = f"{atoms.filename.split('.')[-2]}_{face[0]}{face[1]}{face[2]}_{size[0]}{size[1]}{size[2]}.cif"

    surface = build.surface(atoms, face, size[2], vacuum=vacuum/2)

    if orth:
        #vector = surface[-2].position - surface[-1].position
        #vector = find_vector(surface)
        surface_cell = surface.cell.cellpar()
        ase.visualize.view(surface)
        gamma = surface_cell[-1]
        if gamma != 90:
            a = np.sin(np.radians(gamma)) * surface_cell[0]
            b = surface_cell[1]
            surface_cell[1] = a
            surface_cell[0] = b
            surface_cell[-1] = 90
            #surface.rotate(vector, np.array([1, 0, 0]))
            surface.rotate(-gamma, 'z')
            surface.set_cell(surface_cell)
            surface.wrap()
        o = f"{atoms.filename.split('.')[-2]}_{face[0]}{face[1]}{face[2]}_{size[0]}{size[1]}{size[2]}_orth.cif"

    super_surface = supercell.supercell(surface, size[0], size[1], 1)

    super_surface.write(o)
    out_err.cell_output(super_surface)
    out_err.path_output(o)


if __name__ == '__main__':
    main()
