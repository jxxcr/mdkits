"""
filename: cp2k_input_parsing.py
function: prase cp2k file
"""


import sys
from mdkits.util import os_operation, out_err


def parse_cell():
    """
    function: parse cell information from cp2k input file
    parameter:
        cp2k_input_file: filename of cp2k input
    return:
        cell: list with 6 number
    """
    for file in os_operation.default_input():
        try:
            with open(file, 'r') as f:
                cell = []
                for line in f:
                    if "ABC" in line:
                        xyz = line.split()[-3:]
                        cell.extend(xyz)
                    if "ALPHA_BETA_GAMMA" in line:
                        abc = line.split()[-3:]
                        cell.extend(abc)
                if len(cell) == 3:
                    cell.extend([90.0, 90.0, 90.0])

                out_err.cell_output(cell)
                return cell
        except FileNotFoundError:
            sys.exit(f"cant parse cell information from {','.join(os_operation.default_input())}, assign a cell")


#def get_cell(cp2k_input_file, cell=None):
#    if cell is None:
#        cell = parse_cell(cp2k_input_file)
#    else:
#        cell = cell
#        if len(cell) == 3:
#            cell.extend([90.0, 90.0, 90.0])
#
#    return cell
