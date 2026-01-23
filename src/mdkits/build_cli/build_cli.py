import click
#from mdkits.cli.build import (
#    build_bulk,
#    build_surface,
#    adsorbate,
#)
from mdkits.build_cli import (
    build_bulk,
    build_surface,
    adsorbate,
    build_solution,
    cut_surface,
    supercell,
    build_interface,
    dope,
)


@click.group(name='build')
@click.pass_context
def cli_build(ctx):
    """kits for building"""
    pass


cli_build.add_command(build_bulk.main)
cli_build.add_command(build_surface.main)
cli_build.add_command(adsorbate.main)
cli_build.add_command(build_solution.main)
cli_build.add_command(cut_surface.main)
cli_build.add_command(supercell.main)
cli_build.add_command(build_interface.main)
cli_build.add_command(dope.main)

if __name__ == '__main__':
    cli_build()