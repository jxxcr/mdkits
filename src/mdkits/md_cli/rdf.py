import MDAnalysis as mda
from MDAnalysis.analysis import rdf
import numpy as np
import click
from scipy import integrate
from mdkits.util import arg_type


def calculate_Gab(r_values, gab_values):
    dr = r_values[1] - r_values[0]

    integrand = 4 * np.pi * r_values**2 * gab_values

    G_ab = np.cumsum(integrand) * dr

    return G_ab


@click.command(name="rdf")
@click.argument("filename", type=click.Path(exists=True))
@click.option('--cell', type=arg_type.Cell, help='set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c')
@click.option("--group", type=click.Tuple([str, str]), help="two group to analysis")
@click.option('--range', type=click.Tuple([float, float]), help="the range of rdf")
@click.option('-r', type=arg_type.FrameRange, help='range of frame to analysis')
def main(filename, cell, group, range, r):
    """analysis the radial distribution function"""
    u = mda.Universe(filename)
    u.trajectory.ts.dt = 0.0001
    u.dimensions = cell
    o = f"rdf_{'_'.join(group).replace(' ', '_')}.dat"

    rho = 32/(9.86**3)

    group1 = u.select_atoms(group[0])
    group2 = u.select_atoms(group[1])

    crdf = rdf.InterRDF(group1, group2, verbose=True, range=(range[0], range[1]), norm='rdf')


    if r is not None:
        if len(r) == 2:
            crdf.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            crdf.run(start=r[0], stop=r[1], step=r[2])
    else:
        crdf.run()

    combin = np.column_stack((crdf.results.bins, crdf.results.rdf, calculate_Gab(crdf.results.bins, crdf.results.rdf)*rho))
    np.savetxt(o, combin, header="A\tgr\tNr", fmt="%.5f", delimiter='\t')


if __name__ == "__main__":
    main()