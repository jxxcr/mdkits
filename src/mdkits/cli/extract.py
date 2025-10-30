#!/usr/bin/env python3

# extract final structure form pos.xyz file

import os
import click
from mdkits.util import os_operation, arg_type, out_err
import MDAnalysis
from MDAnalysis import Universe


def write_to_xyz(u, frames, o, select, cut=None):
    ag = u.select_atoms(select)
    with MDAnalysis.Writer(o, ag.atoms.n_atoms, format='XYZ') as w:
        for ts in u.trajectory:
            if ts.frame in frames:
                w.write(ag)
    if cut:
        with open(o, 'r') as fi, open(o+'t', 'w') as fo:
            for i, line in enumerate(fi):
                if i >= cut:
                    fo.write(line)
        os.replace(o+'t', o)


def write_to_xyz_s(u, frames, select, cut=None):
    index = 0
    ag = u.select_atoms(select)
    if select:
        dir = f'./coord/{"_".join(select.split())}'
    else:
        dir = './coord/all'
    for ts in u.trajectory:
        if ts.frame in frames:
            o = f'{dir}/coord_{index:03d}'
            with MDAnalysis.Writer(o, ag.atoms.n_atoms, format='XYZ') as w:
                w.write(ag)
                index += 1
            if cut:
                with open(o, 'r') as fi, open(o+'t', 'w') as fo:
                    for i, line in enumerate(fi):
                        if i >= cut:
                            fo.write(line)
                os.replace(o+'t', o)

@click.command(name='extract')
@click.argument('input_file_name', type=click.Path(exists=True), default=os_operation.default_file_name('*-pos-1.xyz', last=True))
@click.option('-r', type=arg_type.FrameRange, help='frame range to slice', default='-1', show_default=True)
@click.option('-c', help='output a coord.xyz', is_flag=True)
@click.option("--select", type=str, help="select atoms to extract", default="all", show_default=True)
def main(input_file_name, r, c, select):
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
        if select:
            dir = f'./coord/{"_".join(select.split())}'
        else:
            dir = './coord/all'
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            import shutil
            shutil.rmtree(dir)
            os.makedirs(dir)
        write_to_xyz_s(u, frames, select, cut=cut)
        click.echo(os.path.abspath(dir))
    else:
        o = f"{os.path.basename(u.filename).split('.')[0]}_{'_'.join([str(i) for i in r])}_{'_'.join(select.split()) if select else 'all'}.xyz"
        write_to_xyz(u, frames, o, select, cut=cut)
        out_err.path_output(o)


if __name__ == '__main__':
    main()
