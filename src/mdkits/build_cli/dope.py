import click
from mdkits.util import arg_type, encapsulated_ase
import numpy as np


@click.command(name='dope')
@click.argument('atoms', type=arg_type.Structure)
@click.option('--group', type=str, required=True, help='group to dope')
@click.option('--element', type=str, required=True, help='element to dope in some times')
@click.option('--times', type=int, default=1, help='number of atoms to dope')
@click.option('--seed', type=int, default=20000203, help='random seed')
def main(atoms, group, element, times, seed):
    """Dope atoms in the structure"""
    np.random.seed(seed)

    u = encapsulated_ase.atoms_to_u(atoms)
    u.dimensions = atoms.cell.cellpar()

    atomgroup = u.select_atoms(f"{group}")
    if atomgroup.n_atoms == 0:
        raise ValueError(f"No atoms found for group: {group}")
    selected_indices = np.random.choice(atomgroup.indices, size=times, replace=False)
    for idx in selected_indices:
        u.atoms[idx].element = element

    element, count = np.unique(u.select_atoms("all").elements, return_counts=True)
    o = f"{atoms.filename.split('.')[0]}_{'-'.join([f'{e}{c}' for e, c in zip(element, count)])}_doped.cif"

    encapsulated_ase.u_to_cif(u, o)