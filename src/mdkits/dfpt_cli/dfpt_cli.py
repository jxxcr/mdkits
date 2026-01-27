import click
from mdkits.dfpt_cli import (
    elastic,
)


@click.group(name='dfpt')
@click.pass_context
def main(ctx):
    """kits for dfpt analysis"""
    pass


main.add_command(elastic.main)

if __name__ == '__main__':
    main()