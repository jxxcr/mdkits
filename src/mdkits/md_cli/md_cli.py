import click
from mdkits.util import arg_type, os_operation
from mdkits.md_cli import (
    dipole,
    angle,
    density,
    hb_distribution,
    rdf,
)


@click.group(name='md')
@click.pass_context
def cli(ctx, cell, surface, update_water, distance, angle, r):
    """kits for MD analysis"""

cli.add_command(density.main)
cli.add_command(dipole.main)
cli.add_command(angle.main)
cli.add_command(hb_distribution.main)
cli.add_command(rdf.main)


if __name__ == '__main__':
    cli()