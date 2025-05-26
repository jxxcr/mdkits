"""
output and error for cli
"""

import numpy as np
import sys, os


def cell_output(atoms):
    cell = atoms.cell.cellpar()
    if not hasattr(atoms, "name"):
        atoms.name = "present"
    print(f"{atoms.name} cell: x = {cell[0]}, y = {cell[1]}, z = {cell[2]}, a = {cell[3]}\u00B0, b = {cell[4]}\u00B0, c = {cell[5]}\u00B0")


def path_output(file: str):
    print(os.path.abspath(file))

def check_cell(atoms, cell=None):
    if cell is not None:
        atoms.set_cell(cell)
        cell_output(atoms)
    elif not np.array_equal(atoms.cell.cellpar(), np.array([0., 0., 0., 90., 90., 90.])):
        cell_output(atoms)
    elif np.array_equal(atoms.cell.cellpar(), np.array([0., 0., 0., 90., 90., 90.])) and cell is not None:
        atoms.set_cell(cell)
        cell_output(atoms)
    else:
        raise ValueError("can't parse cell please use --cell set cell")