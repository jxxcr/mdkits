import numpy as np
import click
import MDAnalysis
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdkits.util import (
    arg_type,
    numpy_geo,
    encapsulated_mda,
    os_operation
)
from .setting import common_setting
import sys


class Dipole_distribution(AnalysisBase):
    def __init__(self, filename, cell, update_water, distance_judg, angle_judg, surface, dt=0.001, bin_size=0.2):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell

        self.u = u
        self.atomgroup = u.select_atoms("all")
        self.bin_size = bin_size
        self.frame_count = 0
        self.surface = surface
        self.update_water = update_water
        self.mid_z = u.dimensions[2] / 2

        if self.update_water:
            self.distance_judg = distance_judg
            self.angle_judg = angle_judg

        if surface is not None:
            self.surface_group = self.atomgroup.select_atoms(f"{surface}")
            if self.surface_group.n_atoms == 0:
                sys.exit("Please specify the correct surface group")
        else:
            self.surface_group = False

        super(Dipole_distribution, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        self.bin_num = int(self.u.dimensions[2] / self.bin_size) + 2
        self.dipole_distribution = np.zeros(self.bin_num, dtype=np.float64)
        self.o_count = np.zeros(self.bin_num, dtype=np.float64)

        if self.surface_group:
            self.surface_pos = np.zeros(2)

    def _append(self, angle, z):
        bins = np.floor(z / self.bin_size).astype(int) + 1
        np.add.at(self.dipole_distribution, bins, angle)
        np.add.at(self.o_count, bins , 1)

    def _single_frame(self):
        o_group = self.atomgroup.select_atoms("name O")

        if self.update_water:
            h_group = self.atomgroup.select_atoms("name H")
            o, oh1, oh2 = encapsulated_mda.update_water(self, o_group, h_group, distance_judg=self.distance_judg, angle_judg=self.angle_judg, return_index=False)
        else:
            o = o_group
            oh1 = self.atomgroup[o.indices + 1]
            oh2 = self.atomgroup[o.indices + 2]

        if self.surface_group:
            lower_z, upper_z = numpy_geo.find_surface(self.surface_group.positions[:, 2])
            self.surface_pos[0] += lower_z
            self.surface_pos[1] += upper_z

        vec1 = MDAnalysis.lib.distances.minimize_vectors(oh1.positions - o.positions, self.u.dimensions)
        vec2 = MDAnalysis.lib.distances.minimize_vectors(oh2.positions - o.positions, self.u.dimensions)

        bisector = numpy_geo.vector_between_two_vector(vec1, vec2)


        angle_bisector = np.hstack((bisector[o.positions[:, 2] < self.mid_z][:, 2] / np.linalg.norm(bisector[o.positions[:, 2] < self.mid_z], axis=1), -bisector[o.positions[:, 2] > self.mid_z][:, 2] / np.linalg.norm(bisector[o.positions[:, 2] > self.mid_z], axis=1)))

        self._append(angle_bisector, np.hstack((o.positions[:, 2][o.positions[:, 2] < self.mid_z], o.positions[:, 2][o.positions[:, 2] > self.mid_z])))

        self.frame_count += 1

    def _conclude(self):
        if self.frame_count > 0:
            average_dipole = self.dipole_distribution / self.o_count
            water_density = (self.o_count * (15.999+1.0008*2) * 1.660539 / (self.u.dimensions[0] * self.u.dimensions[1] * self.bin_size)) / self.frame_count
            average_dipole = average_dipole * water_density
            bins_z = np.arange(len(average_dipole)) * self.bin_size + self.bin_size / 2

            if self.surface:
                lower_z = self.surface_pos[0] / self.frame_count
                if self.surface_pos[1] == 0:
                    upper_z = np.inf
                else:
                    upper_z = self.surface_pos[1] / self.frame_count

                mask = (bins_z >= lower_z) & (bins_z <= upper_z)
                filtered_bins_z = bins_z[mask] - lower_z
                filtered_dipole_distribution = average_dipole[mask]

                conbined_data = np.column_stack((filtered_bins_z, filtered_dipole_distribution))
            else:
                conbined_data = np.column_stack((bins_z, average_dipole))

            np.savetxt("dipole_distribution.dat", conbined_data, header="z\tDipole Z Positions\tWater Density", fmt='%.5f', delimiter='\t')


@click.command(name="dipole")
@common_setting
def main(filename, cell, update_water, distance, angle, surface, r):
    """analysis dipole along z-axis"""
    a = Dipole_distribution(filename, cell, update_water, distance_judg=distance, angle_judg=angle, surface=surface)
    if r is not None:
        if len(r) == 2:
            a.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            a.run(start=r[0], stop=r[1], step=r[2])
    else:
        a.run()


if __name__ == "__main__":
    main()