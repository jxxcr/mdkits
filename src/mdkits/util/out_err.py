"""
output and error for cli
"""

import numpy as np
import sys


def cell_output(cell: list):
    print(f"system cell: x = {cell[0]}, y = {cell[1]}, z = {cell[2]}, a = {cell[3]}\u00B0, b = {cell[4]}\u00B0, c = {cell[5]}\u00B0")


def check_cell(atoms, cell):
    if np.array_equal(atoms.cell.cellpar(), np.array([0., 0., 0., 90., 90., 90.])) and cell is not None:
        atoms.set_cell(cell)
    else:
        raise ValueError("can't parse cell please use --cell set cell")