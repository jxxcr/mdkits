#!/usr/bin/env python3

# extract final structure form pos.xyz file

import os
import click
from mdkits.util import os_operation, arg_type
import MDAnalysis
from MDAnalysis import Universe


def write_to_xyz(u, frames, o, cut=None):
    with MDAnalysis.Writer(o, u.atoms.n_atoms, format='XYZ') as w:
        for ts in u.trajectory:
            if ts.frame in frames:
                w.write(u)
    if cut:
        with open(o, 'r') as fi, open(o+'t', 'w') as fo:
            for i, line in enumerate(fi):
                if i >= cut:
                    fo.write(line)
        os.replace(o+'t', o)


def write_to_xyz_s(u, frames, cut=None):
    index = 0
    for ts in u.trajectory:
        if ts.frame in frames:
            o = f'./coord/coord_{index:03d}'
            with MDAnalysis.Writer(o, u.atoms.n_atoms, format='XYZ') as w:
                w.write(u)
                index += 1
            if cut:
                with open(o, 'r') as fi, open(o+'t', 'w') as fo:
                    for i, line in enumerate(fi):
                        if i >= cut:
                            fo.write(line)
                os.replace(o+'t', o)

@click.command(name='extract')
@click.argument('input_file_name', type=click.Path(exists=True), default=os_operation.default_file_name('*-pos-1.xyz', last=True))
@click.option('-o', type=str, help='output file name', default='extracted.xyz', show_default=True)
@click.option('-r', type=arg_type.FrameRange, help='frame range to slice', default='-1', show_default=True)
@click.option('-c', help='output a coord.xyz', is_flag=True)
def main(input_file_name, o, r, c):
    """
    extract frames in trajectory file
    """

    u = Universe(input_file_name)
    if len(r) == 1:
        print(f"frame range slice is {r}")
        group = u.trajectory[r]
    else:
        print(f"frame range slice is {slice(*r)}")
        group = u.trajectory[slice(*r)]
    click.echo(f"total frames is {len(u.trajectory)}")
    frames = [ts.frame for ts in group]

    if c:
        cut = 2
    else:
        cut = None

    if len(r) == 3 and r[-1] is not None:
        if not os.path.exists('./coord'):
            os.makedirs('./coord')
        else:
            import shutil
            shutil.rmtree('./coord')
            os.makedirs('./coord')
        write_to_xyz_s(u, frames, cut=cut)
        click.echo(os.path.abspath('./coord'))
    else:
        write_to_xyz(u, frames, o, cut=cut)
        click.echo(os.path.abspath(o))


if __name__ == '__main__':
    main()
