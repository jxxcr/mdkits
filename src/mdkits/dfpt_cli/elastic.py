import click, json
from pymatgen.analysis import elasticity
from mdkits.util import arg_type, encapsulated_ase
import numpy as np


def voigt_to_tensor(C_voigt):

    voigt_map = {
        0: (0, 0),
        1: (1, 1),
        2: (2, 2),
        3: (1, 2),
        4: (0, 2),
        5: (0, 1),
    }

    C_tensor = np.zeros((3, 3, 3, 3))

    for alpha in range(6):
        for beta in range(6):
            i, j = voigt_map[alpha]
            k, l = voigt_map[beta]

            value = C_voigt[alpha, beta]

            for ii, jj in [(i, j), (j, i)]:
                for kk, ll in [(k, l), (l, k)]:
                    C_tensor[ii, jj, kk, ll] = value
                    C_tensor[kk, ll, ii, jj] = value

    return C_tensor


@click.command(name='elastic')
@click.argument('structure', type=arg_type.Structure)
@click.argument('ela_data', type=click.Path(exists=True))
@click.option('--cell', type=arg_type.Cell, help='set cell, a list of lattice: --cell x,y,z or x,y,z,a,b,c')
def main(structure, ela_data, cell):
    if cell:
        structure.set_cell(cell)

    stru = encapsulated_ase.atoms_to_pymatgen_structure(structure)

    data = np.loadtxt(ela_data)
    tensor = voigt_to_tensor(data*100)

    elasitic_tensor = elasticity.ElasticTensor(tensor)
    elasitic_properties = elasitic_tensor.get_structure_property_dict(stru)
    elasitic_properties.pop('structure')

    text = json.dumps(elasitic_properties, indent=4)

    print(text)
    with open('elasitic_properties.json', 'w') as f:
        f.write(text)