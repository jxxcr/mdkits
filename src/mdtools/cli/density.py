#!/usr/bin/env python3

import numpy as np
import click
import MDAnalysis
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdtool.util import cp2k_input_parsing, numpy_geo, encapsulated_mda
import warnings
warnings.filterwarnings("ignore")


class Density_distribution(AnalysisBase):
    def __init__(self, filename, cell, o, distance_judg, angle_judg, dt=0.001, bin_size=0.2, return_index=False):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell

        self.u = u
        self.o = o
        self.distance_judg = distance_judg
        self.angle_judg = angle_judg
        self.atomgroup = u.select_atoms("all")
        self.mid_z = u.dimensions[2]/2
        self.bin_size = bin_size
        self.frame_count = 0
        self.return_index = return_index

        super(Density_distribution, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        self.bin_num = int(self.u.dimensions[2] / self.bin_size) + 2
        self.density_distribution = np.zeros(self.bin_num, dtype=np.float64)
        if self.surface:
            self.surface_pos = ()

    def _append(self, z):
        bins = np.floor(z / self.bin_size).astype(int) + 1
        np.add.at(self.density_distribution, bins, 1)

    def _single_frame(self):
        if self.water:
            o_group = self.atomgroup.select_atoms("name O")
            h_group = self.atomgroup.select_atoms("name H")

            o, oh1, oh2 = encapsulated_mda.update_water(self, o_group, h_group, distance_judg=self.distance_judg, angle_judg=self.angle_judg, return_index=self.return_index)

            self._append(o.positions[:, 2])

        else:
            group = self.atomgroup.select_atoms(f"name {self.element}")
            self._append(group.positions[:, 2])

        self.
        self.frame_count += 1

    def _conclude(self):
        if self.frame_count > 0:
            V = self.u.dimensions[0] * self.u.dimensions[1] * self.bin_size

            if self.water:
                density_distribution = (self.density_distribution * (15.999+1.008*2) * 1.660539 / V) / self.frame_count
            else:
                density_distribution = (self.density_distribution * (10000/6.02) / V) / self.frame_count

            bins_z = np.arange(len(self.density_distribution)) * self.bin_size

            surface = self.find_surface(self.atomgroup.select_atoms("name Pt"))

            lower_z, upper_z = surface
            mask = (bins_z >= lower_z) & (bins_z <= upper_z)
            filtered_bins_z = bins_z[mask] - lower_z
            filtered_density_distribution = density_distribution[mask]
            conbined_data = np.column_stack((filtered_bins_z, filtered_density_distribution))

            np.savetxt(self.o, conbined_data, header="Z\tdensity", fmt='%.5f', delimiter='\t')

@click.command(name='density')
@click.argument('filename', type=click.Path(exists=True), default=os_operation.default_file_name('*-pos-1.xyz', last=True))
@click.option('--cell', type=arg_type.Cell, help='set xyz file cell, --cell x,y,z,a,b,c')
@click.option('--cell', type=arg_type.Cell, help='set cell from cp2k input file or a list of lattice: --cell x,y,z or x,y,z,a,b,c', default='input.inp', show_default=True)
@click.option('-o', type=str, help='output file name', default='density.dat', show_default=True)
def main(filename, cell, o):
    density_dist = Density_distribution(filename, cell, o=o)
    density_dist.run()


if __name__ == '__main__':
    main()
