import click
from . import cp2k_input_parsing


class CellType(click.ParamType):
    name = "pbc cell type"

    def convert(self, value, param, ctx):
        if isinstance(value, str):
            cell = [float(x) for x in value.split(',')]

            if len(cell) == 3:
                click.echo(f"system cell: x = {cell[0]}, y = {cell[1]}, z = {cell[2]}, a = {90}\u00B0, b = {90}\u00B0, c = {90}\u00B0")
                return cell + [90, 90, 90]
            elif len(cell) == 6:
                click.echo(f"system cell: x = {cell[0]}, y = {cell[1]}, z = {cell[2]}, a = {cell[3]}\u00B0, b = {cell[4]}\u00B0, c = {cell[5]}\u00B0")
                return cell
            elif value is None:
                cp2k_input_parsing.parse_cell()
            else:
                self.fail(f"{value} is not a valid cell parameter", param, ctx)


Cell = CellType()