#!/usr/bin/env python3

import numpy as np
import click
import MDAnalysis
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdkits.util import numpy_geo, encapsulated_mda
import warnings, sys
from .setting import common_setting
warnings.filterwarnings("ignore")


class Hb_distribution(AnalysisBase):
    def __init__(self, filename, cell, surface, update_water, distance_judg, angle_judg, hb_distance, hb_angle, bin_size=0.2, dt=0.001, index=None):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell
        self.u = u
        self.atomgroup = u.select_atoms("all")
        self.hb_distance = hb_distance
        self.hb_angle = hb_angle
        self.bin_size = bin_size
        self.surface = surface
        self.update_water = update_water
        self.frame_count = 0
        np.set_printoptions(threshold=np.inf)

        if surface is not None:
            self.surface_group = self.atomgroup.select_atoms(f"{surface}")
            if self.surface_group.n_atoms == 0:
                sys.exit("Please specify the correct surface group")
        else:
            self.surface_group = False

        if self.update_water:
            self.distance_judg = distance_judg
            self.angle_judg = angle_judg
        
        if index is not None:
            self.index = index
            self.hb_d_index = 0
            self.hb_a_index = 0
        else:
            self.index = None

        super(Hb_distribution, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        bin_num = int(self.u.dimensions[2] / self.bin_size) + 2
        self.accepter = np.zeros(bin_num, dtype=np.float64)
        self.donor = np.zeros(bin_num, dtype=np.float64)
        self.od = np.zeros(bin_num, dtype=np.float64)
        if self.surface_group:
            self.surface_pos = np.zeros(2)

    def _append(self, hb_d, hb_a, o):
        bins_d = np.floor(hb_d / self.bin_size).astype(int) + 1
        bins_a = np.floor(hb_a / self.bin_size).astype(int) + 1
        bins_o = np.floor(o / self.bin_size).astype(int) + 1

        bins_d = bins_d[bins_d < len(self.donor)]
        bins_a = bins_a[bins_a < len(self.accepter)]
        bins_o = bins_o[bins_o < len(self.od)]

        np.add.at(self.donor, bins_d, 1)
        np.add.at(self.accepter, bins_a, 1)
        np.add.at(self.od, bins_o, 1)

    def _single_frame(self):
        if self.update_water:
            o = self.atomgroup.select_atoms("name O")
            h = self.atomgroup.select_atoms("name H")

            o_group, oh1, oh2 = encapsulated_mda.update_water(self, o, h, distance_judg=self.distance_judg, angle_judg=self.angle_judg, return_index=False)

            o_pair = MDAnalysis.lib.distances.capped_distance(o_group.positions, o_group.positions, min_cutoff=0, max_cutoff=self.hb_distance, box=self.u.dimensions, return_distances=False)

            o0 = o_group[o_pair[:, 0]]
            o1 = o_group[o_pair[:, 1]]

            o0h1 = oh1[o_pair[:, 0]]
            o0h2 = oh2[o_pair[:, 0]]
            o1h1 = oh1[o_pair[:, 1]]
            o1h2 = oh2[o_pair[:, 1]]
        else:
            o_group = self.atomgroup.select_atoms("name O")
            o_pair = MDAnalysis.lib.distances.capped_distance(o_group.positions, o_group.positions, min_cutoff=0, max_cutoff=self.hb_distance, box=self.u.dimensions, return_distances=False)

            o0 = o_group[o_pair[:, 0]]
            o1 = o_group[o_pair[:, 1]]

            o0h1 = self.atomgroup[o0.indices + 1]
            o0h2 = self.atomgroup[o0.indices + 2]
            o1h1 = self.atomgroup[o1.indices + 1]
            o1h2 = self.atomgroup[o1.indices + 2]

        angle_o0h1_o0_o1 = np.degrees(
            MDAnalysis.lib.distances.calc_angles(o0h1.positions, o0.positions, o1.positions, box=self.u.dimensions)
        )
        angle_o0h2_o0_o1 = np.degrees(
            MDAnalysis.lib.distances.calc_angles(o0h2.positions, o0.positions, o1.positions, box=self.u.dimensions)
        )
        angle_o1h1_o1_o0 = np.degrees(
            MDAnalysis.lib.distances.calc_angles(o1h1.positions, o1.positions, o0.positions, box=self.u.dimensions)
        )
        angle_o1h2_o1_o0 = np.degrees(
            MDAnalysis.lib.distances.calc_angles(o1h2.positions, o1.positions, o0.positions, box=self.u.dimensions)
        )

        condition_d = (angle_o0h1_o0_o1 < self.hb_angle) | (angle_o0h2_o0_o1 < self.hb_angle)
        condition_a = (angle_o1h1_o1_o0 < self.hb_angle) | (angle_o1h2_o1_o0 < self.hb_angle)

        if self.index is not None:
            self.hb_d_index += o0.positions[:, 2][condition_d & (o0.indices == self.index)].shape[0]
            self.hb_a_index += o0.positions[:, 2][condition_a & (o0.indices == self.index)].shape[0]
        else:
            hb_d = o0.positions[:, 2][condition_d]
            hb_a = o0.positions[:, 2][condition_a]

            self._append(hb_d, hb_a, o_group.positions[:, 2])

        if self.surface_group:
            surface = numpy_geo.find_surface(self.surface_group.positions[:, 2])
            self.surface_pos[0] += surface[0]
            self.surface_pos[1] += surface[1]

        self.frame_count += 1

    def _conclude(self):
        if self.frame_count > 0 and self.index is None:
            average_od = self.od / self.frame_count
            average_donor = np.nan_to_num((self.donor / self.frame_count) / average_od, nan=0)
            average_accepter = np.nan_to_num((self.accepter / self.frame_count) / average_od, nan=0)
            average_sum = average_donor + average_accepter

            bins_z = np.arange(len(self.donor)) * self.bin_size + self.bin_size / 2

            if self.surface:
                lower_z = self.surface_pos[0] / self.frame_count
                if self.surface_pos[1] == 0:
                    upper_z = np.inf
                else:
                    upper_z = self.surface_pos[1] / self.frame_count

                mask = (bins_z >= lower_z) & (bins_z <= upper_z)
                filtered_bins_z = bins_z[mask] - lower_z
                filtered_average_accepter = average_accepter[mask]
                filtered_average_donor = average_donor[mask]
                filtered_average_sum = average_sum[mask]

                combined_data = np.column_stack((filtered_bins_z, filtered_average_accepter, filtered_average_donor, filtered_average_sum))
            else:
                combined_data = np.column_stack((bins_z, average_accepter, average_donor, average_sum))

            np.savetxt("hb_distribution.dat", combined_data, header="Z\tAccepter\tDonor\tAccepter+Donor", fmt='%.5f', delimiter='\t')

        if self.index is not None and self.frame_count > 0:
            self.hb_d_index /= self.frame_count
            self.hb_a_index /= self.frame_count
            output = f"# {self.index}\naccepter     : {self.hb_a_index}\ndonor        : {self.hb_d_index}\ntotal        : {self.hb_a_index + self.hb_d_index}"
            with open(f"hb_{self.index}.dat", "a") as f:
                f.write(output)
            print(output)


@click.command(name="hb", help="analysis hydrogen bond distribution along z-axis")
@common_setting
@click.option('--hb_param', type=click.Tuple([float, float]), help='parameter for hydrogen bond', default=(3.5, 35), show_default=True)
@click.option('--index', type=int, help='index of an atom')
def main(filename, hb_param, cell, surface, r, update_water, distance, angle, index):
    """analysis hydrogen bond distribution along z-axis"""
    hb_dist = Hb_distribution(filename, cell, surface, update_water=update_water, distance_judg=distance, angle_judg=angle, hb_distance=hb_param[0], hb_angle=hb_param[1], index=index)

    if r is not None:
        if len(r) == 2:
            hb_dist.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            hb_dist.run(start=r[0], stop=r[1], step=r[2])
    else:
        hb_dist.run()


if __name__ == '__main__':
    main()