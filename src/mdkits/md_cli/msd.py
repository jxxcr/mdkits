import click
import MDAnalysis as mda
import MDAnalysis.analysis.msd as msd
import numpy as np


@click.command(name="msd")
@click.argument("filename", type=click.Path(exists=True))
@click.argument('type', type=click.Choice(['xyz', 'xy', 'yz', 'xz', 'x', 'y', 'z']))
@click.argument("group", type=str)
def main(filename, type, group):
    """analysis msd along the given axis"""
    u = mda.Universe(filename)
    MSD = msd.EinsteinMSD(u, select=group, msd_type=type, fft=True)
    MSD.run(verbose=True)

    data = np.arange(1, MSD.n_frames + 1).reshape(-1, 1)
    s = "_"
    name = f"{s.join(group.split(' '))}"
    header = ''
    for i in range(MSD.n_particles):
        data = np.concatenate((data, MSD.results.msds_by_particle[:, i].reshape(-1, 1)), axis=1)
        header += name + f"_{i}\t"

    np.savetxt(f"msd_{type}.dat", data, fmt="%.5f", delimiter="\t", header=f"frame\t{header}")



if __name__ == '__main__':
    main()