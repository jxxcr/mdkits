import click
import MDAnalysis as mda
import MDAnalysis.analysis.msd as msd
import numpy as np
from mdkits.util import arg_type


@click.command(name="msd")
@click.argument("filename", type=click.Path(exists=True))
@click.argument('type', type=click.Choice(['xyz', 'xy', 'yz', 'xz', 'x', 'y', 'z']))
@click.argument("group", type=str)
@click.option('-r', type=arg_type.FrameRange, help='range of frame to analysis')
def main(filename, type, group, r):
    """analysis msd along the given axis"""
    u = mda.Universe(filename)
    MSD = msd.EinsteinMSD(u, select=group, msd_type=type, fft=True)
    if r is not None:
        if len(r) == 2:
            MSD.run(start=r[0], stop=r[1], verbose=True)
        elif len(r) == 3:
            MSD.run(start=r[0], stop=r[1], step=r[2], verbose=True)
    else:
        MSD.run(verbose=True)

    data = np.arange(1, MSD.n_frames + 1).reshape(-1, 1)
    s = "_"
    name = f"{s.join(group.split(' '))}"
    o = f"msd_{type}_{name}.dat"
    header = ''
    msd_cols = []
    for i in range(MSD.n_particles):
        msd_cols.append(MSD.results.msds_by_particle[:, i].reshape(-1, 1))
        header += name + f"_{i}\t"
    msd_array = np.concatenate(msd_cols, axis=1)
    mean_col = np.mean(msd_array, axis=1, keepdims=True)
    data = np.concatenate((data, mean_col, msd_array), axis=1)
    header = "frame\tmean\t" + header

    np.savetxt(o, data, fmt="%.5f", delimiter="\t", header=header)



if __name__ == '__main__':
    main()