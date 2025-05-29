import click
from .setting import common_setting
import MDAnalysis
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdkits.util import arg_type, numpy_geo
import numpy as np
import sys


class Monitor(AnalysisBase):
    def __init__(self, filename, cell, index, surface, dt=0.001):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell

        self.u = u
        self.atomgroup = self.u.select_atoms("all")
        self.surface = surface

        if index is None:
            sys.exit("Please specify at least one atom to monitor")
        else:
            self.index = index
            self.group = " or ".join([ f"index {i}" for i in self.index ])

        if surface is not None:
            self.surface_group = self.atomgroup.select_atoms(f"{surface}")
            if self.surface_group.n_atoms == 0:
                sys.exit("Please specify the correct surface group")
        else:
            self.surface_group = False

        super(Monitor, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        self.height = []
        if len(self.index) == 2:
            self.distance = []
        elif len(self.index) == 3:
            self.distance = []
            self.angle = []
    
    def _single_frame(self):
        if self.surface_group:
            surface = numpy_geo.find_surface(self.surface_group.positions[:, 2])
        else:
            surface = [0]

        self.height.append(self.atomgroup.select_atoms(self.group).positions[:, 2] - surface[0])

        if len(self.index) == 2:
            vec = MDAnalysis.lib.distances.minimize_vectors(self.atomgroup[self.index[0]].position - self.atomgroup[self.index[1]].position, self.u.dimensions)

            self.distance.append(np.linalg.norm(vec))

        if len(self.index) == 3:
            vec1 = MDAnalysis.lib.distances.minimize_vectors(self.atomgroup[self.index[0]].position - self.atomgroup[self.index[1]].position, self.u.dimensions)
            vec2 = MDAnalysis.lib.distances.minimize_vectors(self.atomgroup[self.index[2]].position - self.atomgroup[self.index[1]].position, self.u.dimensions)

            self.distance.append(np.array([np.linalg.norm(vec1), np.linalg.norm(vec2)]))
            self.angle.append(numpy_geo.vector_vector_angle(vec1, vec2))

    def _conclude(self):
        frame_count = np.arange(self.u.trajectory.n_frames).reshape(-1, 1)

        self.height = np.vstack(self.height)

        np.savetxt("monitor.dat", np.hstack((frame_count, self.height)), fmt="%.5f", header=f"frame\t{'  '.join(self.atomgroup.select_atoms(self.group).names)}")

        if len(self.index) == 2:
            self.distance = np.vstack(self.distance)

            np.savetxt("monitor.dat", np.hstack((frame_count, self.height, self.distance)), fmt="%.5f", header=f"frame\t\t{'  '.join(self.atomgroup.select_atoms(self.group).names)}\t{self.atomgroup.names[self.index[0]]}-{self.atomgroup.names[self.index[1]]}")
        elif len(self.index) == 3:
            self.distance = np.vstack(self.distance)
            self.angle = np.vstack(self.angle)

            np.savetxt("monitor.dat", np.hstack((frame_count, self.height, self.distance, self.angle)), fmt="%.5f", header=f"frame\t\t{'  '.join(self.atomgroup.select_atoms(self.group).names)}\t{self.atomgroup.names[self.index[0]]}-{self.atomgroup.names[self.index[1]]}\t{self.atomgroup.names[self.index[2]]}-{self.atomgroup.names[self.index[1]]}\t{self.atomgroup.names[self.index[0]]}-{self.atomgroup.names[self.index[1]]}-{self.atomgroup.names[self.index[2]]}")


@click.command(name="monitor")
@click.argument("filename", type=click.Path(exists=True))
@click.option("--index", "-i", type=int, help="index of atom to monitor", multiple=True)
@click.option('--cell', type=arg_type.Cell, help="set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c")
@click.option("--surface", type=str, help="surface group")
@click.option('-r', type=arg_type.FrameRange, help='range of frame to analysis')
def main(filename, cell, index, surface, r):
    """
    monitor the property of between atoms
    """
    a = Monitor(filename, cell, index, surface)
    if r is not None:
        if len(r) == 2:
            a.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            a.run(start=r[0], stop=r[1], step=r[2])
    else:
        a.run()
    
    

if __name__ == "__main__":
    main()