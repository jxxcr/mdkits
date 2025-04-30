"""
filename: encapsulated_ase.py
function: some encapsulated ase method
"""


from ase.io import iread, read
import io
import numpy as np
from ase.io.cube import read_cube_data
import MDAnalysis


def wrap_to_cell(chunk, cell, name, big=False):
    """
    function: encapsulated ase.Atom.wrap method
    parameter:
        chunk: a list of frame of structure
        cell: a list of cell parameter
        name: path of temp file to write
        big: make 3X3X1 supercell
    return:
        write into a temp file
    """
    # wrap a chunk of .xyz sturcture in a cell, and write wraped structure to file
    if len(chunk) > 1:
        atoms = iread(io.StringIO('\n'.join(chunk)), format='xyz')
    else:
        atoms = iread(chunk, format='xyz')
    with open(name, 'w') as f:
        f.write('')
    for atom in atoms:
        atom.set_cell(cell)
        atom.set_pbc(True)
        atom.wrap()
        if big:
            from ase.build import make_supercell
            P = [ [3, 0, 0], [0, 3, 0], [0, 0, 1] ]
            atom = make_supercell(atom, P)
        atom.write(f'{name}', append='a', format='xyz')


def rdf(chunk, cell, bin_size, name, parallel=True):
    """
    not used
    """
    from ase.geometry.analysis import Analysis
    from math import ceil
    n = ceil(cell[2] / bin_size)
    if parallel:
        atoms = iread(io.StringIO('\n'.join(chunk)), format='xyz')
    else:
        atoms = iread(chunk, format='xyz')
    atom_list = []
    for atom in atoms:
        atom.set_cell(cell)
        atom.set_pbc(True)
        atom_list.append(atom)
    print(len(atom_list))
    ana = Analysis(atom_list)
    rdf = ana.get_rdf(3.5, n, elements=['O'])
    rdf_array = np.vstack(rdf)
    rdf_array = np.mean(rdf_array, axis=0)
    print(name)
    np.save(name, rdf_array)
    ana.clear_cache()


def ave_cube(filepath):
    """
    function: average hartree file in z_coordinate
    parameter:
        filepath: hartree cube file path
    return:
        z_cube_data: a list of cube data alone z axes
        z_coordinates: a list of coordinates of z axes
    """
    # read data from filepath
    data, atoms = read_cube_data(filepath)
    # define need parameter
    npoints = data.shape[2]
    step_size = atoms.cell[2, 2] / ( npoints - 1 )
    # average hartree file, and calculate z_coordinates
    z_coordinates = [i * step_size for i in range(npoints)]
    z_cube_data = data[:, :, :].sum(axis=(0, 1)) / ( data.shape[0] * data.shape[1] )
    return np.column_stack((z_coordinates, z_cube_data))


def atoms_read_with_cell(file_name, cell=None, coord_mode=False, default_cell=np.array([0., 0., 0., 90., 90., 90.])):
    """
    function: read structure file return a Atoms object with cell
    parameter:
        file_name: structure file name
        cell: cell list
        coord_mode: if file name is coord format
        default_cell: default cell of Atoms object
    return:
        atoms: Atoms object with cell
    """
    import sys, os
    from . import cp2k_input_parsing, structure_parsing

    if coord_mode:
        xyz = structure_parsing.coord_to_xyz(file_name)
        atoms = read(io.StringIO('\n'.join(xyz)), format='xyz')
    else:
        atoms = jread(file_name)

    if cell == None:
        cp2k_cell_file_name = ( 'cell.inc', 'setup.inp', 'input.inp' )
        existing_cell_file = [ file for file in cp2k_cell_file_name if os.path.isfile(file) ]
        if existing_cell_file:
            cell = cp2k_input_parsing.parse_cell(existing_cell_file[0])

    if np.array_equal(atoms.cell.cellpar(), default_cell):
        if cell != None:
            atoms.set_cell(cell)
            print('cell: \n' + ', '.join(map(str, atoms.cell.cellpar())))
            return atoms
        else:
            print("no cell")
            sys.exit(1)
    print('cell: \n' + ', '.join(map(str, atoms.cell.cellpar())))
    return atoms


def jread(filepath):
    from ase.io import read
    suffix = filepath.split('.')[-1]
    if suffix == 'data':
        atom = read(filepath, format='lammps-data', atom_style='atomic')
    else:
        atom = read(filepath)

    return atom


def atoms_to_u(atoms):
    virtual_file = io.StringIO()
    cell = atoms.cell.cellpar()
    atoms.write(virtual_file, format='xyz')

    u = MDAnalysis.Universe(virtual_file, format='xyz')
    u.dimensions = cell

    return u