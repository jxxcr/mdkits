from pymatgen.io.cp2k import outputs
import click
from mdkits.util import arg_type
from pymatgen.electronic_structure.core import Spin
import pandas as pd
import numpy as np


@click.command(name='pdos')
@click.argument('filename', type=arg_type.FileList, default='*-k*.*')
@click.option('--no-reference', is_flag=True, help='if specified, reference energy will not be shifted to fermi level')
@click.option('-o', type=str, help='output file name')
def main(filename, no_reference, o):
    total_dict = {}
    for file in filename:
        dos = outputs.parse_pdos(file, total=True)
        
        pdos = dos[0]
        tdos = dos[1]
        element = list(pdos.keys())[0]
        data_dict = {}
        steplen = 0.1
        fermi = pdos[element][list(pdos[element].keys())[0]].efermi

        energies = pdos[element][list(pdos[element].keys())[0]].energies
        n_min = np.floor((energies.min() - fermi) / steplen)
        n_max = np.ceil((energies.max() - fermi) / steplen)
        integers = np.arange(n_min, n_max + 1)
        bins = fermi + integers * steplen

        dos, ener = np.histogram(energies, bins=bins, weights=tdos.get_densities(Spin.up), range=(energies[0], energies[-1]))
        data_dict['energy'] = ener[:-1] + steplen/2


        df = pd.DataFrame(data_dict)

        df['total'] = 0
        for orb_key in pdos[element].keys():
            data_obj = pdos[element][orb_key]
            weights = data_obj.get_densities(Spin.up)
            dos, ener = np.histogram(energies, bins=bins, weights=weights, range=(energies[0], energies[-1]))
            df[orb_key] = dos/steplen
            df['total'] += dos/steplen


        if Spin.down in pdos[element][list(pdos[element].keys())[0]].densities:
            df['total_down'] = 0
            for orb_key in pdos[element].keys():
                data_obj = pdos[element][orb_key]
                weights = data_obj.get_densities(Spin.down)
                dos, ener = np.histogram(energies, bins=bins, weights=weights, range=(energies[0], energies[-1]))
                df[f'{orb_key}_down'] = dos/steplen
                df['total_down'] += dos/steplen

        if o is None:
            out_filename = f"{element}.pdos"
        else:
            out_filename = o

        total_dict[element] = df

        if not no_reference:
            df['energy'] = df['energy'] - fermi

        with open(out_filename, 'w') as f:
            header = '#' + ' '.join([str(key) for key in df.columns]) + '\n'
            f.write(header)
            df.to_csv(f, sep='\t', index=False, header=False)


    energy = list(total_dict.values())[0]['energy']

    total_dos = 0
    for element, df in total_dict.items():
        total_dos += df['total']

    total_df = pd.DataFrame({'energy': energy, 'total': total_dos})

    
    with open('total.pdos', 'w') as f:
        header = '# energy total_dos' + '\n'
        f.write(header)
        total_df.to_csv(f, sep='\t', index=False, header=False)