import click
from mdkits.cli import (
    build_bulk,
    build_surface,
)


@click.group(name='build')
@click.pass_context
def cli_build(ctx):
    """kits for building"""
    pass


cli_build.add_command(build_bulk.main)
cli_build.add_command(build_surface.main)

if __name__ == '__main__':
    cli_build()