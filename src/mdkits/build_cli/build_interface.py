import click
from mdkits.util import arg_type, out_err


@click.command(name="interface")
@click.option('--slab', type=arg_type.Structure, help='surface')
@click.option('--sol', type=arg_type.Structure, help='solution')
@click.option('--interval', type=float, help='interval between surface and sol', default=2, show_default=True)
@click.option('--cap', type=click.Choice(['ne', 'slab']), help='build slab interface')
@click.option('--vacuum', type=float, help='vacuum length', default=0, show_default=True)
def main(slab, sol, interval, cap, vacuum):
    """build interface"""
    out_err.check_cell(slab)
    out_err.check_cell(sol)

    o = f"{slab.filename.split('.')[-2]}_{sol.filename.split('.')[-2]}.cif"

    slab.set_pbc(True)
    slab.center()
    slab_cell = slab.cell.cellpar()
    init_slab_cell = slab.cell.cellpar()
    if cap == 'slab':
        slab_copy = slab.copy()

    sol_cell = sol.cell.cellpar()

    interface_cell = [max(slab_cell[0], sol_cell[0]), max(slab_cell[1], sol_cell[1]), max(slab_cell[2], sol_cell[2]), max(slab_cell[3], sol_cell[3]), max(slab_cell[4], sol_cell[4]), max(slab_cell[5], sol_cell[5])]

    sol.set_pbc(True)
    sol.center()
    sol.positions[:, 2] += slab_cell[2] + interval

    slab.extend(sol)
    slab_cell[2] += 2 * interval + sol_cell[2]
    slab.set_cell(slab_cell)
    slab.center()

    if cap is None:
        slab.positions[:, 2] -= 0.5 * init_slab_cell[2]
    elif cap == 'ne':
        from ase import Atoms
        ne_interval = 4
        lenx = init_slab_cell[0]
        leny = init_slab_cell[1]
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

        slab.positions[:, 2] += -(slab_cell[2] + interval)
        slab.extend(ne_atoms)
        slab_cell[2] += ne_cell[2]
        slab.set_cell(slab_cell)
        slab.center()
    elif cap == 'slab':
        slab.positions[:, 2] += -(slab_cell[2] + interval)
        slab.extend(slab_copy)
        slab_cell[2] += slab_copy.cell.cellpar()[2]
        slab.set_cell(slab_cell)
        slab.center()
    
    slab_cell[0] = interface_cell[0]
    slab_cell[1] = interface_cell[1]
    if vacuum > 0:
        slab_cell[2] += vacuum
        slab.set_cell(slab_cell)


    slab.write(o)
    out_err.path_output(o)

if __name__ == '__main__':
    main()