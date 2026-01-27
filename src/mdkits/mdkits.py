import click
from mdkits.build_cli import build_cli
from mdkits.dft_cli import dft_cli
from mdkits.dfpt_cli import dfpt_cli
from mdkits.md_cli import md_cli
from mdkits.cli import (
    convert,
    extract,
    data,
    plot,
)


@click.group(name='cli')
@click.pass_context
@click.version_option()
def cli(ctx):
    """kits for md or dft"""
    pass


cli.add_command(md_cli.cli)
cli.add_command(build_cli.cli_build)
cli.add_command(dft_cli.main)
cli.add_command(dfpt_cli.main)
cli.add_command(convert.main)
cli.add_command(extract.main)
cli.add_command(data.main)
cli.add_command(plot.main)


if __name__ == '__main__':
    cli()