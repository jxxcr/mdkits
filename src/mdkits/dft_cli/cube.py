#!/usr/bin/env python3

import numpy as np
import click
from mdkits.util import encapsulated_ase, os_operation


def ave_cube_data(cube_data, range):
	mask = (cube_data[:,0] >= range[0]) & (cube_data[:,0] <=range[1])
	bulk_cube_data = cube_data[mask]
	ave_cube_data = np.mean(bulk_cube_data[:,1])
	return ave_cube_data


@click.command(name='cube')
@click.argument('filename', type=click.Path(exists=True), default=os_operation.default_file_name('*.cube', last=True))
@click.option('-b', '--bulk_range', type=(float, float), help='parameter to calculate mean value of bulk', default=None)
@click.option('-o', type=str, help='output file name, default is "cube.out"', default='cube.out', show_default=True)
def main(filename, bulk_range, o):
	"""
	analysis cube file
	"""

	cube_data = encapsulated_ase.ave_cube(filename)

	## if bulk range is exit, out put a difference of cube_data
	if bulk_range is not None:
		bulk_cube_data = ave_cube_data(cube_data, bulk_range)
		print(bulk_cube_data)
		np.savetxt(o, cube_data, header=f'Z\tcube_data\t area average is: {bulk_cube_data}')
	
	else:
		np.savetxt(o, cube_data, header='Z\tcube_data')

	


if __name__ == '__main__':
	main()