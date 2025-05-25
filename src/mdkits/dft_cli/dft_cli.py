import click
from mdkits.dft_cli import (
    cube,
    pdos,
)


@click.group(name='dft')
@click.pass_context
def main(ctx):
    """kits for dft analysis"""
    pass


main.add_command(cube.main)
main.add_command(pdos.main)

if __name__ == '__main__':
    main()