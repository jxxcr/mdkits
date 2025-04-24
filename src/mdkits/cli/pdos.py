#!/usr/bin/env python3

from cp2kdata import Cp2kPdos
import click
import numpy as np
from mdkits.util import os_operation


# set argument
@click.command(name='pdos')
@click.argument('filename', type=list, default=os_operation.default_file_name('*-k*.pdos'))
@click.option('-t', '--type', type=str, default='total', show_default=True)
@click.option('-c', '--clos', type=tuple)
def main(filename, type, clos):
    if type == 'total':
        dos_obj = Cp2kPdos(filename[0])
        dos, ener = dos_obj.get_raw_dos(dos_type=type)
        print(f"analysis of total dos is done")
        np.savetxt('total.pdos', np.column_stack((ener, dos)), header='energy\tdos')
    else:
        if type:
            for file in filename:
                dos_obj = Cp2kPdos(file)
                dos, ener = dos_obj.get_raw_dos(dos_type=type)
                print(f"analysis of {file}'s {type} dos is done")
                np.savetxt(f'{dos_obj.read_dos_element()}_{type}.pdos', np.column_stack((ener, dos)), header='energy\tdos')

        if clos:
            for file in filename:
                dos_obj = Cp2kPdos(file)
                dos, ener = dos_obj.get_raw_dos(usecols=clos)
                print(f"analysis of {file}'s {type} dos is done")
                np.savetxt(f'{dos_obj.read_dos_element()}_{"_".join(clos)}.pdos', np.column_stack((ener, dos)), header='energy\tdos')


if __name__ == '__main__':
    main()