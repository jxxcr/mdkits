#!/usr/bin/env python3

import numpy as np
import argparse
import MDAnalysis
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from util import cp2k_input_parsing
import warnings
warnings.filterwarnings("ignore")


class Hb_distribution(AnalysisBase):
    def __init__(self, filename, cell, surface, dt=0.001, hb_distance=3.5, hb_angle=35, bin_size=0.2):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell
        self.u = u
        self.atomgroup = u.select_atoms("all")
        self.hb_distance = hb_distance
        self.hb_angle = hb_angle
        self.bin_size = bin_size
        self.surface = surface
        self.frame_count = 0
        super(Hb_distribution, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        bin_num = int(self.u.dimensions[2] / self.bin_size) + 2
        self.donor = np.zeros(bin_num, dtype=np.float64)

    def _append(self, hb_d):
        bins_d = np.floor(hb_d / self.bin_size).astype(int) + 1

        bins_d = bins_d[bins_d < len(self.donor)]

        np.add.at(self.donor, bins_d, 1)

        self.frame_count += 1

    def _single_frame(self):
        o_group = self.atomgroup.select_atoms("name O")
        o_pair = MDAnalysis.lib.distances.capped_distance(o_group.positions, o_group.positions, min_cutoff=0, max_cutoff=self.hb_distance, box=self.u.dimensions, return_distances=False)

        o0 = o_group[o_pair[:, 0]]
        o1 = o_group[o_pair[:, 1]]

        o0h1 = self.atomgroup[o0.indices + 1]
        o0h2 = self.atomgroup[o0.indices + 2]

        angle_o0h1_o0_o1 = np.degrees(
            MDAnalysis.lib.distances.calc_angles(o0h1.positions, o0.positions, o1.positions, box=self.u.dimensions)
        )
        angle_o0h2_o0_o1 = np.degrees(
            MDAnalysis.lib.distances.calc_angles(o0h2.positions, o0.positions, o1.positions, box=self.u.dimensions)
        )

        mid_z = (self.surface[0] + self.surface[1]) / 2

        condition_d = ((angle_o0h1_o0_o1 < self.hb_angle) | (angle_o0h2_o0_o1 < self.hb_angle)) & (o0.positions[:, 2] - o1.positions[:, 2] > 0)
        #condition_d = ((angle_o0h1_o0_o1 < self.hb_angle) | (angle_o0h2_o0_o1 < self.hb_angle)) & (((o0.positions[:, 2] < mid_z) & (o0.positions[:, 2] - o1.positions[:, 2] > 0)) | ((o0.positions[:, 2] > mid_z) & (o0.positions[:, 2] - o1.positions[:, 2] < 0)))
        #condition_a = ((angle_o1h1_o1_o0 < self.hb_angle) | (angle_o1h2_o1_o0 < self.hb_angle)) & (((o1.positions[:, 2] < mid_z) & (o1.positions[:, 2] - o0.positions[:, 2] > 1.5)) | ((o1.positions[:, 2] > mid_z) & (o1.positions[:, 2] - o0.positions[:, 2] < -1.5)))

        hb_d = (o0.positions[:, 2][condition_d] + o1.positions[:, 2][condition_d]) / 2
        #hb_a = (o0.positions[:, 2][condition_a] + o1.positions[:, 2][condition_a]) / 2

        self._append(hb_d)

    def _conclude(self):
        if self.frame_count > 0:
            average_donor = self.donor / self.frame_count

        bins_z = np.arange(len(self.donor)) * self.bin_size

        lower_z, upper_z = self.surface
        mask = (bins_z >= lower_z) & (bins_z <= upper_z)
        filtered_bins_z = bins_z[mask] - lower_z
        filtered_average_donor = average_donor[mask]

        combined_data = np.column_stack((filtered_bins_z, filtered_average_donor))

        filename = 'hb_distribution_down.dat'
        np.savetxt(filename, combined_data, header="Z\tDonor", fmt='%.5f', delimiter='\t')


def parse_data(s):
    return [float(x) for x in s.replace(',', ' ').split()]


def parse_r(s):
    return [int(x) for x in s.replace(':', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description="analysis hb distribution")
    parser.add_argument('filename', type=str, help='filename to analysis')
    parser.add_argument('--cp2k_input_file', type=str, help='input file name of cp2k, default is "input.inp"', default='input.inp')
    parser.add_argument('-r', type=parse_r, help='range of analysis', default=[0, -1, 1])
    parser.add_argument('--cell', type=parse_data, help='set cell, a list of lattice, --cell x,y,z or x,y,z,a,b,c')
    parser.add_argument('--surface', type=parse_data, help='[down_surface_z, up_surface_z]')
    parser.add_argument('--hb_param', type=parse_data, help='[hb_distance, hb_angle], default is [3.5, 35]', default=[3.5, 35])

    return parser.parse_args()


def main():
    args = parse_argument()
    cell = cp2k_input_parsing.get_cell(args.cp2k_input_file, args.cell)

    hb_dist = Hb_distribution(args.filename, cell, args.surface, hb_distance=args.hb_param[0], hb_angle=args.hb_param[1])
    hb_dist.run(start=args.r[0], stop=args.r[1], step=args.r[2])


if __name__ == '__main__':
    main()
