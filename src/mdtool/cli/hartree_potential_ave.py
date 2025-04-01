#!/usr/bin/env python3

################################################
# averange cp2k output(or some else file correspond to ase.io.read_cube_data) hartree.cube to z coordinate with python
## file path is need to pay attention
## cycle parameter is need to pay attention
## buck range is need to pay attention
################################################

from ase.io.cube import read_cube_data
import numpy as np
import argparse

def array_type(string):
	number_list = string.split(',')
	number_array = np.array(number_list, dtype=int)
	return number_array


def ave_potential(filepath):
	# is to average hartree file in z_coordinate
	
	## read data from filepath
	data, atoms = read_cube_data(filepath)
	
	## define need parameter
	npoints = data.shape[2]
	step_size = atoms.cell[2, 2] / ( npoints - 1 )
	
	## average hartree file, and calculate z_coordinates
	z_coordinates = [i * step_size for i in range(npoints)]
	z_potential = 27.2114 * data[:, :, :].sum(axis=(0, 1)) / ( data.shape[0] * data.shape[1] )
	return z_potential, z_coordinates


def buck_potential(xaxe, potential, range):
	mix = np.concatenate((xaxe.reshape(-1, 1), potential.reshape(-1, 1)), axis=1)
	mask = (mix[:,0] >= range[0]) & (mix[:,0] <=range[1])
	buck_potential = mix[mask]
	ave_potential = np.mean(buck_potential[:,1])
	return ave_potential


# set argument
parser = argparse.ArgumentParser(description='to handle cp2k output file hartree cube, name should be "hartree-*.cube"')
parser.add_argument('folder_path', type=str, help='folder that contain all hartree cube file')
parser.add_argument('cyc_range', type=array_type, help='cycle parameter, need to seperate with ",", similar with range() -- 1,201  1,201,10')
parser.add_argument('-b', '--buck_range', type=array_type, help='parameter to calculate mean value of buck', default=None)
parser.add_argument('-o', type=str, help='output file name, default is "out.put"', default='hartree.out')

args = parser.parse_args()


## init output potential file's shape, and define a z axe
init_array = ave_potential('{}/hartree-{}.cube'.format(args.folder_path, args.cyc_range[0]))
potential = np.empty((0, init_array[0].shape[0]))
z_coordinates = np.array((init_array[1])).reshape(-1, 1)

## average one hartree file
if len(args.cyc_range) == 3:
	for i in range(args.cyc_range[0], args.cyc_range[1], args.cyc_range[2]):
		file_path = '{}/hartree-{}.cube'.format(args.folder_path, i)
		potential = np.append(potential, [ave_potential(file_path)[0]], axis=0)
else:
	for i in range(args.cyc_range[0], args.cyc_range[1]):
		file_path = '{}/hartree-{}.cube'.format(args.folder_path, i)
		potential = np.append(potential, [ave_potential(file_path)[0]], axis=0)

## average every averaged harterr file, and append to z_coordinates
#aved_potential = potential[:, :].sum(axis=0) / len(range(1, 201))
aved = np.mean(potential, axis=0)
total_potential = np.append(z_coordinates, aved.reshape(-1, 1), axis=1)

## if buck range is exit, out put a difference of potential
if args.buck_range is not None:
	buck_potential = buck_potential(z_coordinates, aved, args.buck_range)
	with open(args.o + 'diff', 'w') as f:
		f.write("{}\t{}\t{}".format(aved[0], buck_potential, aved[0]-buck_potential))

## write output
with open(args.o, 'w') as f:
	for value in total_potential:
		f.write(" ".join(map(str, value)) + '\n')

