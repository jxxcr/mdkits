"""
filename: cp2k_input_parsing.py
function: prase cp2k file
"""


import sys


def parse_cell(cp2k_input_file):
    """
    function: parse cell information from cp2k input file
    parameter:
        cp2k_input_file: filename of cp2k input
    return:
        cell: list with 6 number
    """
    try:
        with open(cp2k_input_file, 'r') as f:
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

            print(f"system cell: x = {cell[0]}, y = {cell[1]}, z = {cell[2]}, a = {cell[3]}\u00B0, b = {cell[4]}\u00B0, c = {cell[5]}\u00B0")
            return cell
    except FileNotFoundError:
        print(f'cp2k input file name "{cp2k_input_file}" is not found, assign a cp2k input file or assign a "cell"')
        sys.exit(1)


#def get_cell(cp2k_input_file, cell=None):
#    if cell is None:
#        cell = parse_cell(cp2k_input_file)
#    else:
#        cell = cell
#        if len(cell) == 3:
#            cell.extend([90.0, 90.0, 90.0])
#
#    return cell
