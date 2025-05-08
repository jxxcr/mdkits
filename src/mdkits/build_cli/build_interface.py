import click
from mdkits.util import arg_type, out_err


@click.command(name="interface")
@click.option('--surface', type=arg_type.Structure, help='surface')
@click.option('--sol', type=arg_type.Structure, help='solution')
@click.option('--interval', type=float, help='interval between surface and sol', default=2, show_default=True)
@click.option('--symmetry', is_flag=True, help='build symmetry interface')
@click.option('--ne', type=float, help='add vacuum and Ne as gas phase', default=0, show_default=True)
def main(surface, sol, interval, symmetry, ne):
    """build interface"""
    out_err.check_cell(surface)
    out_err.check_cell(sol)

    o = f"{surface.filename.split('.')[-2]}_{sol.filename.split('.')[-2]}.cif"

    surface.set_pbc(True)
    surface.center()
    surface_cell = surface.cell.cellpar()
    init_surface_cell = surface.cell.cellpar()

    sol_cell = sol.cell.cellpar()
    sol.set_pbc(True)
    sol.center()
    sol.positions += surface[2] + interval

    surface.extend(sol)
    surface_cell[2] += 2 * interval + sol_cell[2]
    surface.set_cell(surface_cell)
    surface.center()

    if symmetry:
        surface.positions -= 0.5 * init_surface_cell[2]
        surface.center()
    elif ne > 0:
        from ase import Atoms
        ne_interval = 4
        lenx = init_surface_cell[0]
        leny = init_surface_cell[1]
        ne_cell = [lenx, leny, 2, 90, 90, 90]
        ne_position = []
        ne_symbols = []
        ne_site = [int(lenx//ne_interval), int(leny//ne_interval)]
        for i in range(ne_site[0]):
            for j in range(ne_site[1]):
                ne_position.append((i*ne_interval, j*ne_interval, 0))
                ne_symbols.append('Ne')
        ne_atoms = Atoms(symbols=ne_symbols, positions=ne_position, cell=ne_cell)
        ne_atoms.center()

        surface.positions += -(surface_cell[2])
        surface.extend(ne_atoms)
        surface_cell[2] += ne_cell[2]
        surface.set_cell(surface_cell)
        surface.center()

    surface.write(o)

if __name__ == '__main__':
    main()