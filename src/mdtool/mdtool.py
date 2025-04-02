import click
from mdtool.cli import (
    convert,
    wrap,
    extract,
    data,
)


@click.group(name='cli')
@click.pass_context
def cli(ctx):
    """mdtool is a tool for managing markdown files."""
    pass


cli.add_command(convert.main)
cli.add_command(wrap.main)
cli.add_command(extract.main)
cli.add_command(data.main)


if __name__ == '__main__':
    cli()