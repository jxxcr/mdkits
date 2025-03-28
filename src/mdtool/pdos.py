#!/usr/bin/env python3.9

# caculate pdos

from cp2kdata import Cp2kPdos
import argparse
import numpy as np
from util import os_operation


def to_file(filename, ener, dos):
	to_file = np.column_stack((ener, dos))
	np.savetxt(filename, to_file, delimiter=" ")


# set argument
parser = argparse.ArgumentParser(description='calculate pdos')
parser.add_argument('filename', type=str, nargs='?', default=os_operation.default_file_name('*-k*.pdos'))
parser.add_argument('--type', type=str, default='total')
args = parser.parse_args()


# pdos
#dos_types = ['0']
#for dos_type in dos_types:
#	for atom_type in range(1, args.type_number+1):
#		dos_obj = Cp2kPdos(f'{args.project_name}-k{atom_type}-1_{args.run_step}.pdos')
#		dos, ener = dos_obj.get_raw_dos()
#		to_file(f"{dos_obj.read_dos_element()}_{dos_type}.pdos", ener, dos)

# total dos
print(args.filename)
for file in args.filename:
    dos_obj = Cp2kPdos(file)
    dos, ener = dos_obj.get_raw_dos(dos_type=args.type)
    to_file(f'{dos_obj.read_dos_element()}_{args.type}.pdos', ener, dos)
