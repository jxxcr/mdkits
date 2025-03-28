#!/usr/bin/env python3

# extract final structure form pos.xyz file

import argparse
import os, sys
from mdtool.util import structure_parsing, os_operation


def parse_range(s):
    range_list = [int(x) for x in s.split(':')]
    if len(range_list) == 1:
        range_list.append(range_list[0]+1)
        range_list.append(None)
    if len(range_list) == 2:
        range_list.append(None)
    return slice(range_list[0], range_list[1], range_list[2])



# set argument
def parse_argument():
    parser = argparse.ArgumentParser(description='extract pos file from output file')

    parser.add_argument('input_file_name', type=str, nargs='?', help='input file name', default=os_operation.default_file_name('*-pos-1.xyz', last=True))
    parser.add_argument('-o', type=str, help='output file name, default is "out.xyz"', default='extracted.xyz')
    parser.add_argument('-r', type=parse_range, help='list range', default=slice(-1, None, None))
    parser.add_argument('-c', help='output a coord.xyz', action='store_true')
    parser.add_argument('-s', type=int, help='separated output', default=None)

    return parser.parse_args()


def main():
    args = parse_argument()
    if args.input_file_name == None:
        print('give a xyz file')
        sys.exit()
    groups = structure_parsing.xyz_to_groups(args.input_file_name)
    print(f"total frame is {len(groups)}")
    sliced_groups = groups[args.r]

    if args.s:
        sliced_groups = groups[1::args.s]
        if not os.path.exists('./coord'):
            os.makedirs('./coord')
        else:
            import shutil
            shutil.rmtree('./coord')
            os.makedirs('./coord')
        for index, group in enumerate(sliced_groups):
            if args.c:
                structure_parsing.group_to_xyz(f'./coord/coord_{index:03d}', group, cut=2)
            else:
                structure_parsing.group_to_xyz(f'./coord/coord_{index:03d}', group)
    else:
        if args.c:
            structure_parsing.groups_to_xyz(args.o, sliced_groups, cut=2)
        else:
            structure_parsing.groups_to_xyz(args.o, sliced_groups)
        print(os.path.abspath(args.o))


if __name__ == '__main__':
    main()
