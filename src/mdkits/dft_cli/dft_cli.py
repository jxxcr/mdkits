import click
from mdkits.dft_cli import (
    cube,
    pdos,
    fix,
    pdos2,
)


@click.group(name='dft')
@click.pass_context
def main(ctx):
    """kits for dft analysis"""
    pass


main.add_command(cube.main)
main.add_command(pdos.main)
main.add_command(fix.main)
main.add_command(pdos2.main)

if __name__ == '__main__':
    main()