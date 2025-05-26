import click
from mdkits.md_cli import (
    density,
    hb_distribution,
    angle,
)


@click.group(name='md')
@click.pass_context
def main(ctx):
    """kits for MD analysis"""
    pass

main.add_command(density.main)
main.add_command(hb_distribution.main)
main.add_command(angle.main)


if __name__ == '__main__':
    main()