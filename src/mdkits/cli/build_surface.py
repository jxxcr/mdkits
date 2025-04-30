#!/usr/bin/env python3

import click, os
from ase import build
import numpy as np


def surface_check(obj, surface_type):
    if hasattr(obj, surface_type):
        return getattr(obj, surface_type)


@click.command(name='surface')
@click.argument('symbol', type=str)
@click.argument('surface', type=click.Choice(['fcc100', 'fcc110', 'fcc111', 'fcc211', 'bcc100', 'bcc110', 'bcc111', 'hcp0001', 'hcp10m10', 'diamond100', 'diamond111', 'mx2', 'graphene']))
@click.argument('size', type=click.Tuple([int, int, int]))
@click.option('--kind', type=click.Choice(['2H', '1T']), help='designate the kind of MX2 surface')
@click.option('-a', type=float, help='the lattice constant. if specified, it overrides the expermental lattice constant of the element. must be specified if setting up a crystal structure different from the one found in nature')
@click.option('-c', type=float, help='extra hcp lattice constant. if specified, it overrides the expermental lattice constant of the element. Default is ideal ratio: sqrt(8/3)', default=np.sqrt(8/3), show_default=True)
@click.option('--thickness', type=float, help='Thickness of the layer, for mx2 and graphene')
@click.option('--orth', is_flag=True, help='if specified and true, forces the creation of a unit cell with orthogonal basis vectors. if the default is such a unit cell, this argument is not supported')
@click.option('--vacuum', type=float, help='designate vacuum of surface, default is None', default=0.0)
def main(symbol, surface, size, kind, a, c, thickness, orth, vacuum):
    #if args.primitive:
    #    a = args.a * 0.7071 * 2
    #else:
    #    a = args.a

    vacuum = vacuum / 2
    build_surface = surface_check(build, surface)
    out_filename = f"{symbol}_{surface}_{size[0]}{size[1]}{size[2]}.cif"

    if surface in ['hcp0001', 'hcp10m10']:
        atoms = build_surface(symbol, size, a=a, c=c, vacuum=vacuum, orthogonal=orth)
    elif surface in ['mx2']:
        if thickness is None:
            atoms = build_surface(symbol, size, kind=kind, a=a, vacuum=vacuum)
        else:
            atoms = build_surface(symbol, size, kind=kind, a=a, vacuum=vacuum, thickness=thickness)
    elif surface in ['graphene']:
        if a is None:
            a = 2.46

        if thickness is None:
            atoms = build_surface(formula=symbol, size=size, a=a, vacuum=vacuum)
        else:
            atoms = build_surface(formula=symbol, size=size, thickness=thickness, a=a, vacuum=vacuum)
    else:
        atoms = build_surface(symbol, size, a=a, vacuum=vacuum, orthogonal=orth)
    
    atoms.write(out_filename)
    print(os.path.abspath(out_filename))


if __name__ == '__main__':
    main()

