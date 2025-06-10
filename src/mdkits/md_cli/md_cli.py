import click
from mdkits.md_cli import (
    wrap,
    dipole,
    angle,
    density,
    hb_distribution,
    vac,
    rdf,
    msd,
    monitor,
)


@click.group(name='md')
@click.pass_context
def cli(ctx):
    """kits for MD analysis"""

cli.add_command(wrap.main)
cli.add_command(density.main)
cli.add_command(dipole.main)
cli.add_command(angle.main)
cli.add_command(hb_distribution.main)
cli.add_command(vac.main)
cli.add_command(rdf.main)
cli.add_command(msd.main)
cli.add_command(monitor.main)


if __name__ == '__main__':
    cli()