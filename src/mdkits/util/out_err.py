"""
output and error for cli
"""

import numpy as np
import sys, os


def cell_output(cell):
    print(f"system cell: x = {cell[0]}, y = {cell[1]}, z = {cell[2]}, a = {cell[3]}\u00B0, b = {cell[4]}\u00B0, c = {cell[5]}\u00B0")


def path_output(file: str):
    print(os.path.abspath(file))

def check_cell(atoms, cell=None):
    if not np.array_equal(atoms.cell.cellpar(), np.array([0., 0., 0., 90., 90., 90.])):
        cell_output(atoms.cell.cellpar())
    elif np.array_equal(atoms.cell.cellpar(), np.array([0., 0., 0., 90., 90., 90.])) and cell is not None:
        atoms.set_cell(cell)
    else:
        raise ValueError("can't parse cell please use --cell set cell")