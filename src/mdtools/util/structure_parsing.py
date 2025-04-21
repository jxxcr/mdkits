"""
filename: structure_parsing.py
function: prase file with .xyz structue
"""


import numpy as np


def xyz_to_chunks(filename, thread):
    """
    function: split .xyz file to chunks to parallel analysis
    """
    with open(filename, 'r') as f:
        data = f.read()

    #with open(filename, 'r') as f:
    #    atom_number = int(f.readline().split()[0]) + 2

    atom_number = int(data[:data.index('\n') + 1]) + 2
    line_data = data.split('\n')
    chunk_size = (len(line_data) / atom_number) // thread
    chunks = [line_data[i:i+int(chunk_size*atom_number)] for i in range(0, len(line_data), int(chunk_size*atom_number))]
    return chunks


def xyz_to_groups(filename, cut=0):
    """
    function: split .xyz file to groups, every groups is one single frame
    """
    with open(filename, 'r') as f:
        data = f.read()

    # read number of atoms
    end_index = data.index('\n') + 1
    natom = int(data[:end_index]) + 2

    # seqrate file with natom +2
    lines = data.split('\n')
    groups = [lines[i+cut:i+natom] for i in range(0, len(lines), natom)][:-1]
    return groups


def xyz_to_specified_list(filename, atom_range, cut=0):
    """
    function: split .xyz file to specified list, specified atoms position list
    """
    with open(filename, 'r') as f:
        data = f.read()

    # read number of atoms
    end_index = data.index('\n') + 1
    natom = int(data[:end_index]) + 2

    # seqrate file with natom +2
    lines = data.split('\n')
    if len(atom_range) > 1:
        groups = [lines[i+atom_range[0]:i+atom_range[1]] for i in range(0, len(lines), natom)][:-1]
    else:
        groups = [lines[i+atom_range[0]] for i in range(0, len(lines), natom)][:-1]
    return groups


def xyz_to_specified_array(filename, atom_range, cut=0):
    """
    function: split .xyz file to specified list, specified atoms position list
    """
    with open(filename, 'r') as f:
        data = f.read()

    # read number of atoms
    end_index = data.index('\n') + 1
    natom = int(data[:end_index]) + 2

    # seqrate file with natom +2
    lines = data.split('\n')
    if len(atom_range) > 1:
        groups = [lines[i+atom_range[0]:i+atom_range[1]] for i in range(0, len(lines), natom)][:-1]
    else:
        groups = [lines[i+atom_range[0]] for i in range(0, len(lines), natom)][:-1]
    groups = [groups[i][j].split()[1:] for i in range(len(groups)) for j in range(len(groups[i]))]
    return np.array(groups, dtype=np.float64)


def xyz_to_npy(filename):
    """
    function: parse .xyz file to numpy array with float dtype, and cut first column of atom type
    """
    data = xyz_to_groups(filename, cut=2)
    new_data = [[list(map(float, subsublist.split()[1:])) for subsublist in sublist] for sublist in data]
    return np.array(new_data)


def chunk_to_groups(data):
    """
    function: split chunk to single frames
    """
    natom = int(data[0]) + 2
    groups = [data[i:i+natom] for i in range(0, len(data), natom)][:-1]
    return groups


def groups_to_xyz(filename, groups, cut=None):
    """
    function: write groups(some of frame) to .xyz file
    """
    with open(filename, 'w') as f:
        for group in groups:
           for i in group[cut:]:
               f.write(i + '\n')


def group_to_xyz(filename, group, cut=None):
    """
    function: write groups(some of frame) to .xyz file
    """
    with open(filename, 'w') as f:
       for i in group[cut:]:
           f.write(i + '\n')


def coord_to_xyz(filename):
    with open(filename, 'r') as f:
        data = f.read()
    data = data.split('\n')
    data.insert(0, '')
    data.insert(0, str(len(data)-2))
    return data


def atom_mass_parse(group):
    import periodictable
    atom_mass_dict = {}
    names = atom_name_parse()
    for name in names:
        if hasattr(periodictable, name):
            atom = getattr(periodictable, name)
            atom_mass_dict[name] = atom.mass
        else:
            print(f'dont have face named {name}, use mass is 0')
            atom_mass_dict[name] = 0
    return atom_mass_dict


def atom_name_parse(group):
    names = {row.split()[0] for row in group[2:]}
    return names
