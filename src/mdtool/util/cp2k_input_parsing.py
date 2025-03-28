"""
filename: cp2k_input_parsing.py
function: prase cp2k file
"""


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
    except FileNotFoundError:
        print(f'cp2k input file name {cp2k_input_file} is not found, assign a cp2k input file')
    return [float(x) for x in cell]


def get_cell(cp2k_input_file, cell=None):
    if cell is None:
        cell = parse_cell(cp2k_input_file)
    else:
        cell = cell
        if len(cell) == 3:
            cell.extend([90.0, 90.0, 90.0])

    print(f"cell is {cell}")
    return cell
