#!/usr/bin/env python3

import os, sys, argparse
import numpy as np
import math
import multiprocessing
from util import (
    structure_parsing,
    cp2k_input_parsing,
    os_operation,
    atom_count,
    )


def array_type(string):
	number_list = string.split(',')
	number_array = array(number_list, dtype=float)
	return number_array


def get_cell(cp2k_input_file, cell=None):
    if cell is None:
        cell = cp2k_input_parsing.parse_cell(cp2k_input_file)
    else:
        cell = cell
        if len(cell) == 3:
            cell.extend([90.0, 90.0, 90.0])

    return cell


def parse_cell(s):
    if s == None:
        return None
    return [float(x) for x in s.replace(',', ' ').split()]


# set argument
def parse_argument():
    parser = argparse.ArgumentParser(description='calculate water density destribution alone z axis')

    parser.add_argument('input_file_name', type=str, nargs='?', help='input file name', default=os_operation.default_file_name('*-pos-1.xyz', last=True))
    #parser.add_argument('-a', type=str, help='atom to statistic', default='O')
    parser.add_argument('-o', type=str, help='output file name, default is "density.dat"', default='density.dat')
    parser.add_argument('-r', type=array_type, help='bulk range')
    parser.add_argument('--cp2k_input_file', type=str, help='input file name of cp2k, default is "input.inp"', default='input.inp')
    parser.add_argument('--cell', type=parse_cell, help='set cell, a list of lattice, [x,y,z] or [x,y,z,a,b,c]')
    parser.add_argument('--process', type=int, help='paralle process number default is 28', default=28)
    parser.add_argument('--temp', help='keep temp file', action='store_false')

    return parser.parse_args()


def main():
    args = parse_argument()
    bin_size = 0.2
    cell = get_cell(args.cp2k_input_file, args.cell)
    temp_dir = f'{os.environ.get("TEMP_DIR")}/{os.getpid()}'
    os_operation.make_temp_dir(temp_dir, delete=args.temp)
    chunks = structure_parsing.xyz_to_chunks(args.input_file_name, args.process)
    group = structure_parsing.chunk_to_groups(chunks[0])[0]
    atom_names = structure_parsing.atom_name_parse(group)
    for atom_name in atom_names:
        for index, chunk in enumerate(chunks):
            t = multiprocessing.Process(target=atom_count.atom_number_count, args=[chunk, bin_size, cell[2], atom_name, f'{temp_dir}/chunk_{index}.temp'])
            t.start()

        for t in multiprocessing.active_children():
            t.join()

        chunks_array_list = []
        for i in range(len(chunks)):
            chunk_array = np.load(f'{temp_dir}/chunk_{i}.temp.npy')
            chunks_array_list.append(chunk_array)
        chunks_array = np.vstack(chunks_array_list)
        chunks_array = np.mean(chunks_array, axis=0)
        if atom_name == 'O':
            chunks_array = chunks_array * (15.999+1.0080*2) * 1.660539 / (cell[0]*cell[1]*bin_size)
            with open(f'density_water.dat', 'w') as f:
                for i in range(len(chunks_array)):
                    f.write(str((i+1)*bin_size) + '\t' + str(chunks_array[i]) + '\n')

        chunks_array = chunks_array * (10000/6.02) / (cell[0]*cell[1]*bin_size)
        with open(f'density_{atom_name}.dat', 'w') as f:
            for i in range(len(chunks_array)):
                f.write(str((i+1)*bin_size) + '\t' + str(chunks_array[i]) + '\n')

        print(f"density analysis of {atom_name} is done")

if __name__ == '__main__':
    main()
