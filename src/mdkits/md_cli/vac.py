import numpy as np
import click
import MDAnalysis
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdkits.util import os_operation, arg_type


class Velocity_AutoCorrelation(AnalysisBase):
    def __init__(self, filename, select, dt=0.001):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        self.u = u
        self.atomgroup = u.select_atoms(select)

        super(Velocity_AutoCorrelation, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        self.cvv = []
        self.v0 = self.atomgroup.positions
        self.normalize = 1/np.sum(self.v0*self.v0)
        self.cvv.append(np.sum(self.v0*self.v0)*self.normalize)


    def _append(self, cvv):
        self.cvv.append(cvv*self.normalize)

    def _single_frame(self):
        cvv = np.sum(self.atomgroup.positions*self.v0)
        self._append(cvv)

    def _conclude(self):
        self.cvv = np.array(self.cvv)

        sf = self.cvv.shape[0]
        fftraj = np.fft.rfft(self.cvv)
        fdos = np.abs(fftraj)

        faxis = np.fft.rfftfreq(sf, d=1/sf)

        combine = np.column_stack((np.arange(len(self.cvv)), self.cvv))

        np.savetxt('vac.dat', combine, fmt='%.5f', header="frame\tvac")
        np.savetxt('freq.dat', np.column_stack((faxis, fdos)), fmt='%.5f', header="freq\tabundance")


@click.command(name="vac")
@click.argument("filename", type=click.Path(exists=True), default=os_operation.default_file_name('*-vel-1.xyz', last=True))
@click.option("--select", type=str, default="all", help="atom selection", show_default=True)
@click.option('-r', type=arg_type.FrameRange, help='range of frame to analysis')
def main(filename, select, r):
    """analysis velocity autocorrelation function and frequency"""
    a = Velocity_AutoCorrelation(filename, select)

    if r is not None:
        if len(r) == 2:
            a.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            a.run(start=r[0], stop=r[1], step=r[2])
    else:
        a.run()


if __name__ == '__main__':
    main()