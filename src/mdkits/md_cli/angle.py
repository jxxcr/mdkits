import click
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
import MDAnalysis
import sys
from mdkits.util import numpy_geo, encapsulated_mda, arg_type
import numpy as np
from .setting import common_setting


class Angle_distribution(AnalysisBase):
    def __init__(self, filename, cell, water_height, update_water, surface, distance_judg=None, angle_judg=(None, None), dt=0.001, bin_size=5):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell

        self.u = u
        self.atomgroup = u.select_atoms("all")
        self.bin_size = bin_size
        self.frame_count = 0
        self.surface = surface
        self.update_water = update_water
        self.mid_z = u.dimensions[2]/2

        self.normal_up = np.array([0, 0, 1])
        self.normal_down = np.array([0, 0, -1])
        self.total_angle = 180

        if water_height is None:
            sys.exit("Please specify the water height")
        else:
            self.water_height = water_height

        if self.update_water:
            self.distance_judg = distance_judg
            self.angle_judg = angle_judg

        if surface is not None:
            self.surface_group = self.atomgroup.select_atoms(f"{surface}")
            if self.surface_group.n_atoms == 0:
                sys.exit("Please specify the correct surface group")
        else:
            sys.exit("Please specify a surface group")

        super(Angle_distribution, self).__init__(self.atomgroup.universe.trajectory, verbose=True)
    
    def _prepare(self):
        self.bin_num = int(self.total_angle / self.bin_size) + 2
        self.angle_w_distribution = np.zeros(self.bin_num, dtype=np.float64)
        self.angle_oh_distribution = np.zeros(self.bin_num, dtype=np.float64)

    def _append(self, angle, anglew=True):
        bins = np.floor(angle / self.bin_size).astype(int) + 1

        if anglew:
            bins = bins[bins < len(self.angle_w_distribution)]
            np.add.at(self.angle_w_distribution, bins, 1)
        else:
            bins = bins[bins < len(self.angle_oh_distribution)]
            np.add.at(self.angle_oh_distribution, bins, 1)


    def _single_frame(self):
        surface = numpy_geo.find_surface(self.surface_group.positions[:, 2])

        if surface[1] == 0:
            o_group = self.atomgroup.select_atoms(f"name O and prop z < {surface[0]+self.water_height}", updating=True)
        else:
            o_group = self.atomgroup.select_atoms(f"name O and (prop z < {surface[0]+self.water_height} or prop z > {surface[1]-self.water_height})", updating=True)
        
        h_group = self.atomgroup.select_atoms("name H")

        if self.update_water:
            o, oh1, oh2 = encapsulated_mda.update_water(self, o_group=o_group, h_group=h_group, distance_judg=self.distance_judg, angle_judg=self.angle_judg, return_index=False)
        else:
            o = o_group
            oh1 = self.atomgroup[o_group.indices + 1]
            oh2 = self.atomgroup[o_group.indices + 2]

        vec1 = MDAnalysis.lib.distances.minimize_vectors(oh1.positions - o.positions, self.u.dimensions)
        vec2 = MDAnalysis.lib.distances.minimize_vectors(oh2.positions - o.positions, self.u.dimensions)

        bisector = numpy_geo.vector_between_two_vector(vec1, vec2)

        angle_vec1 = np.hstack((numpy_geo.vector_vector_angle(vec1[o.positions[:, 2] < self.mid_z], self.normal_up), numpy_geo.vector_vector_angle(vec1[o.positions[:, 2] > self.mid_z], self.normal_down)))

        angle_vec2 = np.hstack((numpy_geo.vector_vector_angle(vec2[o.positions[:, 2] < self.mid_z], self.normal_up), numpy_geo.vector_vector_angle(vec2[o.positions[:, 2] > self.mid_z], self.normal_down)))

        angle_bisector = np.hstack((numpy_geo.vector_vector_angle(bisector[o.positions[:, 2] < self.mid_z], self.normal_up), numpy_geo.vector_vector_angle(bisector[o.positions[:, 2] > self.mid_z], self.normal_down)))

        self._append(angle_vec1, anglew=False)
        self._append(angle_vec2, anglew=False)
        self._append(angle_bisector)

        self.frame_count += 1

    def _conclude(self):
        if self.frame_count > 0:
            average_angle_w = self.angle_w_distribution / self.frame_count
            average_angle_oh = self.angle_oh_distribution / (self.frame_count*2)
            bins_z = np.arange(len(average_angle_w)) * self.bin_size
            conbined_data = np.column_stack((bins_z, average_angle_w, average_angle_oh))
            np.savetxt("angle_distribution.dat", conbined_data, header="angle\tw_suf_dist\toh_suf_dist", fmt='%.5f', delimiter='\t')


@click.command(name="angle", help="analysis angle between normal vectors and OH vector or bisector")
@common_setting
@click.option("--water_height", type=float, help="water height from surface")
def main(filename, cell, water_height, update_water, distance, angle, surface, r):
    """analysis angle between normal vectors and OH vector or bisector"""
    a = Angle_distribution(filename, cell, water_height, update_water, distance_judg=distance, angle_judg=angle, surface=surface)
    if r is not None:
        if len(r) == 2:
            a.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            a.run(start=r[0], stop=r[1], step=r[2])
    else:
        a.run()


if __name__ == "__main__":
    main()