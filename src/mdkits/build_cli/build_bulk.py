#!/usr/bin/env python3

import click
from ase.build import bulk
import numpy as np


@click.command(name='bulk')
@click.argument('symbol', type=str)
@click.argument('cs', type=click.Choice(['sc', 'fcc', 'bcc', 'tetragonal', 'bct', 'hcp', 'rhombohedral', 'orthorhombic', 'mcl', 'diamond', 'zincblende', 'rocksalt', 'cesiumchloride', 'fluorite', 'wurtzite']))
@click.option('-a', type=float, help='designate lattice constant a')
@click.option('-b', type=float, help='designate lattice constant b. if only a and b is given, b will be interpreted as c instead')
@click.option('-c', type=float, help='designate lattice constant c')
@click.option('--alpha', type=float, help='angle in degrees for rhombohedral lattice')
@click.option('--covera', type=float, help='c/a ratio used for hcp. Default is ideal ratio: sqrt(8/3)', default=np.sqrt(8/3), show_default=True)
@click.option('-u', type=float, help='internal coordinate for Wurtzite structure')
@click.option('--orth', is_flag=True, help='construct orthorhombic unit cell instead of primitive cell which is the default')
@click.option('--cubic', is_flag=True, help='construct cubic unit cell if possible')
def main(symbol, cs, a, b, c, alpha, covera, u, orth, cubic):
    """
    build a bulk structure
    """

    #if args.primitve:
    #    a = args.a * 0.7071 * 2
    #else:
    #    a = args.a
    atoms = bulk(symbol, cs, a=a, b=b, c=c, alpha=alpha, covera=covera, u=u, orthorhombic=orth, cubic=cubic)

    atoms.write(f"{symbol}_{cs}.cif", format='cif')


if __name__ == '__main__':
    main()

