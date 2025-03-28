#!/usr/bin/env python3

import argparse, multiprocessing, os
import numpy as np
from util import (
    structure_parsing,
    numpy_geo,
    os_operation,
    cp2k_input_parsing,
    )


def hb_count(chunk, index, cell, filename, hb_distance=3.5, hb_angle=35):
    groups = structure_parsing.chunk_to_groups(chunk)
    groups_hb_list = []
    coefficients = numpy_geo.cell_to_wrap_coefficients(cell)
    for group in groups:
        group_hb_array = np.zeros((3, 1))
        present_index = index
        o_present = group[present_index].split()
        if o_present[0] == 'O':
            o_present = np.array(o_present[1:], dtype=np.float64)
            group_hb_array[2, 0] += 1
            for other_index in range(2, len(group)):
                o_other = group[other_index].split()
                if o_other[0] == 'O':
                    o_other = np.array(o_other[1:], dtype=np.float64)
                    oo_distance, o_other = numpy_geo.unwrap(o_present, o_other, coefficients, max=0)
                    if oo_distance < hb_distance and oo_distance > 1:
                        _, o_present_h1 = numpy_geo.unwrap(o_present, np.array(group[present_index+1].split()[1:], dtype=np.float64), coefficients)
                        _, o_present_h2 = numpy_geo.unwrap(o_present, np.array(group[present_index+2].split()[1:], dtype=np.float64), coefficients)
                        _, o_other_h1 = numpy_geo.unwrap(o_other, np.array(group[other_index+1].split()[1:], dtype=np.float64), coefficients)
                        _, o_other_h2 = numpy_geo.unwrap(o_other, np.array(group[other_index+2].split()[1:], dtype=np.float64), coefficients)

                        o_present_o_other_h1_angle = numpy_geo.vector_vector_angle(o_present-o_other, o_other_h1-o_other)
                        o_present_o_other_h2_angle = numpy_geo.vector_vector_angle(o_present-o_other, o_other_h2-o_other)
                        if o_present_o_other_h1_angle < hb_angle or o_present_o_other_h2_angle < hb_angle:
                            group_hb_array[0, 0] += 1
                        o_other_o_present_h1_angle = numpy_geo.vector_vector_angle(o_other-o_present, o_present_h1-o_present)
                        o_other_o_present_h2_angle = numpy_geo.vector_vector_angle(o_other-o_present, o_present_h2-o_present)
                        if o_other_o_present_h1_angle < hb_angle or o_other_o_present_h2_angle < hb_angle:
                            group_hb_array[1, 0] += 1
        groups_hb_list.append(group_hb_array)
    groups_hb_array = np.vstack(groups_hb_list)
    group_hb_acc_array = np.sum(groups_hb_array[0::3], axis=0).reshape(1, -1)
    group_hb_don_array = np.sum(groups_hb_array[1::3], axis=0).reshape(1, -1)
    group_hb_num_array = np.sum(groups_hb_array[2::3], axis=0).reshape(1, -1)
    group_hb_array = np.vstack([group_hb_acc_array, group_hb_don_array, group_hb_num_array])
    np.save(filename, group_hb_array)


def parse_data(s):
    return [float(x) for x in s.replace(',', ' ').split()]

def parse_argument():
    parser = argparse.ArgumentParser(description="analysis an O atom's hydrogen bond in water")
    parser.add_argument('index', type=int, help='index of target atom in coord.xyz, or all of hb distribution on z')
    parser.add_argument('input_file_name', type=str, nargs='?', help='input file name', default=os_operation.default_file_name('wraped.xyz', last=True))
    parser.add_argument('--cp2k_input_file', type=str, help='input file name of cp2k, default is "input.inp"', default='input.inp')
    parser.add_argument('--cell', type=parse_data, help='set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c')
    parser.add_argument('--hb_param', type=parse_data, help='[hb_distance, hb_angle], default is [3.5, 35]', default=[3.5, 35])
    parser.add_argument('--process', type=int, help='paralle process number default is 28', default=28)
    parser.add_argument('--temp', help='keep temp file', action='store_false')

    return parser.parse_args()

def main():
    args = parse_argument()
    output = f'./hb_{args.index}.dat'
    cell = cp2k_input_parsing.get_cell(args.cp2k_input_file, args.cell)
    chunks = structure_parsing.xyz_to_chunks(args.input_file_name, args.process)
    temp_dir = f'{os.environ.get("TEMP_DIR")}/{os.getpid()}'
    os_operation.make_temp_dir(temp_dir, delete=args.temp)

    for index, chunk in enumerate(chunks):
        t = multiprocessing.Process(target=hb_count, args=[chunk, args.index, cell, f'{temp_dir}/chunk_{index}.temp'])
        t.start()

    for t in multiprocessing.active_children():
        t.join()

    chunks_array_list = []
    for i in range(len(chunks)):
        chunk_array = np.load(f'{temp_dir}/chunk_{i}.temp.npy')
        chunks_array_list.append(chunk_array)
    chunks_array = np.vstack(chunks_array_list)
    chunks_array = np.mean(chunks_array, axis=1)

    with open(output, 'w') as f:
        f.write(f"# {args.index}\n")
        f.write(f"accepter : {chunks_array[0]:.2f}\n")
        f.write(f"donor    : {chunks_array[1]:.2f}\n")
        f.write(f"total    : {chunks_array[0]+chunks_array[1]:.2f}\n")
    print(f"# {args.index}")
    print(f"accepter : {chunks_array[0]:.2f}")
    print(f"donor    : {chunks_array[1]:.2f}")
    print(f"total    : {chunks_array[0]+chunks_array[1]:.2f}")


if __name__ == '__main__':
    main()
