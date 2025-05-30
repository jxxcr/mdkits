import click, os
from ase.io import read
import numpy as np
from ase.collections import g2
from mdkits.util import os_operation, cp2k_input_parsing, out_err


class CellType(click.ParamType):
    name = "cell type"

    def convert(self, value, param, ctx):
        if isinstance(value, str):
            cell = [float(x) for x in value.split(',')]

            if len(cell) == 3:
                cell += [90, 90, 90]
                return cell
            elif len(cell) == 6:
                return cell
            else:
                self.fail(f"{value} is not a valid cell parameter", param, ctx)


class FrameRangeType(click.ParamType):
    name = "frame range"
    def convert(self, value, param, ctx):
        if isinstance(value, str):
            parts = value.split(':')

            range_list = [int(x) if x else None for x in parts]

            if len(range_list) > 0 and len(range_list) <= 3:
                return range_list
            else:
                self.fail(f"{value} is not a valid frame range", param, ctx)


class StructureType(click.ParamType):
    name = "structure type"
    def convert(self, value, param, ctx):
        no_cell=np.array([0., 0., 0., 90., 90., 90.])
        if isinstance(value, str):
            if os.path.exists(value):
                try:
                    atoms = read(value)
                except:
                    self.fail(f"{value} is not a valid structure file", param, ctx)

                if np.array_equal(atoms.cell.cellpar(), no_cell):
                    cell = cp2k_input_parsing.parse_cell()
                    atoms.set_cell(cell)

                atoms.filename = value.replace('./', '').replace('.\\', '').split('/')[-1]
                return atoms
            else:
                self.fail(f"{value} is not exists", param, ctx)



class MoleculeType(click.Choice):
    name = "mocular type"
    def __init__(self):
        g2.names.append(click.Path(exists=True))
        super().__init__(choices=tuple(g2.names))

class AdsSiteType(click.Choice):
    name = "adsorption site"
    def __init__(self):
        site = ['ontop', 'hollow','fcc', 'hcp', 'bridge', 'shortbridge', 'longbridge']
        super().__init__(choices=tuple(site))



Cell = CellType()
FrameRange = FrameRangeType()
Molecule = MoleculeType()
AdsSite = AdsSiteType()
Structure = StructureType()