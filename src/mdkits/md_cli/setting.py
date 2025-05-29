import click
from mdkits.util import arg_type, os_operation


def common_setting(f):
    f = click.argument('filename', type=click.Path(exists=True), default=os_operation.default_file_name('*-pos-1.xyz', last=True))(f)
    f = click.option('-r', type=arg_type.FrameRange, help='range of frame to analysis')(f)
    f = click.option('--angle', type=(float, float), help='update water angle judgment')(f)
    f = click.option('--distance', type=float, help='update water distance judgment', default=1.2, show_default=True)(f)
    f = click.option('--update_water', is_flag=True, help='update water with distance or angle judgment')(f)
    f = click.option("--surface", type=str, help="surface group")(f)
    f = click.option('--cell', type=arg_type.Cell, help="set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c")(f)

    return f