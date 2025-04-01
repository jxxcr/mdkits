import click
from mdtool.cli import (
    convert,
    wrap
)


@click.group(name='cli', commands=[convert.main, wrap.main], invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """mdtool is a tool for managing markdown files."""
    pass


#cli.add_command(convert.main)
#cli.add_command(wrap.main)


if __name__ == '__main__':
    cli()