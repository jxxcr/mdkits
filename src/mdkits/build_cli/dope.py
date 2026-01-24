import click
from mdkits.util import arg_type, encapsulated_ase
import numpy as np


@click.command(name='dope')
@click.argument('atoms', type=arg_type.Structure)
@click.option('--group', type=str, required=True, help='group to dope')
@click.option('--element', type=(str, int), required=True, help='element and number of element to dope', multiple=True)
@click.option('--seed', type=int, default=20000203, help='random seed')
def main(atoms, group, element, seed):
    """Dope atoms in the structure"""
    np.random.seed(seed)

    u = encapsulated_ase.atoms_to_u(atoms)
    u.dimensions = atoms.cell.cellpar()

    for elementi, times in element:
        atomgroup = u.select_atoms(f"{group}")
        if atomgroup.n_atoms == 0:
            raise ValueError(f"No atoms found for {group} in doping {elementi}")
        if times > atomgroup.n_atoms:
            raise ValueError(f"Cannot dope {times} atoms, only {atomgroup.n_atoms} atoms available in group {group}")
        selected_indices = np.random.choice(atomgroup.indices, size=times, replace=False)
        for idx in selected_indices:
            u.atoms[idx].element = elementi

    element, count = np.unique(u.select_atoms("all").elements, return_counts=True)
    o = f"{atoms.filename.split('.')[0]}_{'-'.join([f'{e}{c}' for e, c in zip(element, count)])}_doped.cif"

    encapsulated_ase.u_to_cif(u, o)