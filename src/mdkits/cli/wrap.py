#!/usr/bin/env python3

import os
from MDAnalysis import Universe
import MDAnalysis, click
from mdkits.util import (
    arg_type,
    os_operation,
    cp2k_input_parsing
    )


@click.command(name='wrap')
@click.argument('filename', type=click.Path(exists=True), default=os_operation.default_file_name('*-pos-1.xyz', last=True))
@click.option('-o', type=str, help='output file name', default='wraped.xyz', show_default=True)
@click.option('--cell', type=arg_type.Cell, help='set cell from cp2k input file or a list of lattice: --cell x,y,z or x,y,z,a,b,c', default='input.inp', show_default=True)
def main(filename, o, cell):
    """
    wrap the coordinates in a cell from a trajectory file
    """

    u = Universe(filename)
    u.dimensions = cell
    ag = u.select_atoms("all")

    with MDAnalysis.Writer(o, ag.n_atoms) as W:
        for ts in u.trajectory:
            ag.wrap()
            W.write(ag)

    click.echo("\nwrap is done, output file {o} is:")
    click.echo(os.path.abspath(o))


if __name__ == '__main__':
    main()
