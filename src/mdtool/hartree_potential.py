#!/usr/bin/env python3

################################################
# averange cp2k output(or some else file correspond to ase.io.read_cube_data) hartree.cube to z coordinate with python
## file path is need to pay attention
## cycle parameter is need to pay attention
## buck range is need to pay attention
################################################

from numpy import empty, array, mean, append, concatenate
from argparse import ArgumentParser
from util import encapsulated_ase, os_operation


def array_type(string):
	number_list = string.split(',')
	number_array = array(number_list, dtype=float)
	return number_array


def buck_potential(xaxe, potential, range):
	mix = concatenate((xaxe.reshape(-1, 1), potential.reshape(-1, 1)), axis=1)
	mask = (mix[:,0] >= range[0]) & (mix[:,0] <=range[1])
	buck_potential = mix[mask]
	ave_potential = mean(buck_potential[:,1])
	return ave_potential


# set argument
parser = ArgumentParser(description='to handle cp2k output file hartree cube, name should be "hartree-*.cube"')
parser.add_argument('file_name', type=str, nargs='?', help='hartree cube file', default=os_operation.default_file_name('*-v_hartree-1_*.cube', last=True))
parser.add_argument('-b', '--buck_range', type=array_type, help='parameter to calculate mean value of buck', default=None)
parser.add_argument('-o', type=str, help='output file name, default is "out.put"', default='hartree.out')

args = parser.parse_args()


## init output potential file's shape, and define a z axe
init_array = encapsulated_ase.ave_potential(args.file_name)
potential = empty((0, init_array[0].shape[0]))
z_coordinates = array((init_array[1])).reshape(-1, 1)

potential = encapsulated_ase.ave_potential(args.file_name)[0]

aved = mean(potential, axis=0)
total_potential = append(z_coordinates, potential.reshape(-1, 1), axis=1)

## if buck range is exit, out put a difference of potential
if args.buck_range is not None:
	buck_potential = buck_potential(z_coordinates, potential, args.buck_range)
	print(buck_potential)
	with open('hartree_potential.dat', 'w') as f:
		f.write(f"{buck_potential}" + '\n')

## write output
with open(args.o, 'w') as f:
	for value in total_potential:
		f.write(" ".join(map(str, value)) + '\n')

