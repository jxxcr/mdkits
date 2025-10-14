#!/usr/bin/env python3

import numpy as np
import click, math
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdkits.util import (
    arg_type,
    numpy_geo,
    encapsulated_mda,
    os_operation,
)
from .setting import common_setting
import warnings, sys
warnings.filterwarnings("ignore")


class Density_distribution(AnalysisBase):
    def __init__(self, filename, cell, o, element, atomic_mass, update_water, distance_judg, angle_judg, surface, dt=0.001, bin_size=0.2, return_index=False):
        u = Universe(filename)
        u.trajectory.ts.dt = dt
        u.dimensions = cell

        self.u = u
        self.atomgroup = u.select_atoms("all")
        self.bin_size = bin_size
        self.frame_count = 0
        self.return_index = return_index
        self.surface = surface
        self.atomic_mass = atomic_mass
        self.update_water = update_water
        self.element = element

        if element is None and update_water is False:
            sys.exit("Please specify the element to analysis or use --update-water option")

        if self.update_water:
            self.distance_judg = distance_judg
            self.angle_judg = angle_judg

        if o == 'density_{element}.dat':
            if self.update_water:
                self.o = "density_water.dat"
            else:
                self.o = f"density_{element.replace(' ', '_')}.dat"
        else:
            self.o = o

        if surface is not None:
            self.surface_group = self.atomgroup.select_atoms(f"{surface}")
            if self.surface_group.n_atoms == 0:
                sys.exit("Please specify the correct surface group")
        else:
            self.surface_group = False

        super(Density_distribution, self).__init__(self.atomgroup.universe.trajectory, verbose=True)

    def _prepare(self):
        self.bin_num = int(self.u.dimensions[2] / self.bin_size) + 2
        self.density_distribution = np.zeros(self.bin_num, dtype=np.float64)
        if self.surface_group:
            self.surface_pos = np.zeros(2)

    def _append(self, z):
        bins = np.floor(z / self.bin_size).astype(int) + 1
        np.add.at(self.density_distribution, bins, 1)


    def _single_frame(self):
        if self.update_water:
            o_group = self.atomgroup.select_atoms("name O")
            h_group = self.atomgroup.select_atoms("name H")

            o, oh1, oh2 = encapsulated_mda.update_water(self, o_group, h_group, distance_judg=self.distance_judg, angle_judg=self.angle_judg, return_index=self.return_index)

            self._append(o.positions[:, 2])

        else:
            group = self.atomgroup.select_atoms(f"{self.element}", updating=True)
            self._append(group.positions[:, 2])

        if self.surface_group:
            surface = numpy_geo.find_surface(self.surface_group.positions[:, 2])
            self.surface_pos[0] += surface[0]
            self.surface_pos[1] += surface[1]

        self.frame_count += 1

    def _conclude(self):
        if self.frame_count > 0:
            V = self.u.dimensions[0] * self.u.dimensions[1] * math.sin(math.radians(180 - self.u.dimensions[-1])) * self.bin_size

            if self.atomic_mass:
                density_distribution = (self.density_distribution * self.atomic_mass * 1.660539 / V) / self.frame_count
            else:
                density_distribution = (self.density_distribution * (10000/6.02) / V) / self.frame_count

            bins_z = np.arange(len(self.density_distribution)) * self.bin_size + self.bin_size / 2

            if self.surface:
                lower_z = self.surface_pos[0] / self.frame_count
                if self.surface_pos[1] == 0:
                    upper_z = np.inf
                else:
                    upper_z = self.surface_pos[1] / self.frame_count

                mask = (bins_z >= lower_z) & (bins_z <= upper_z)
                filtered_bins_z = bins_z[mask] - lower_z
                filtered_density_distribution = density_distribution[mask]

                conbined_data = np.column_stack((filtered_bins_z, filtered_density_distribution))
            else:
                conbined_data = np.column_stack((bins_z, density_distribution))

            np.savetxt(self.o, conbined_data, header="Z\tdensity", fmt='%.5f', delimiter='\t')

@click.command(name='density', help="analysis density or concentration of element in a trajectory file")
@common_setting
@click.option('--group', type=str, help='group to analysis')
@click.option('--atomic_mass', type=float, help='output density unit (g/cm3), should give atomic mass of element, else is concentration unit (mol/L)')
@click.option('-o', type=str, help='output file name', default='density_{element}.dat', show_default=True)
def main(filename, cell, o, group, atomic_mass, update_water, distance, angle, surface, r):
    """
    analysis density or concentration of element in a trajectory file
    """

    density_dist = Density_distribution(filename, cell, o=o, distance_judg=distance, angle_judg=angle, element=group, atomic_mass=atomic_mass, update_water=update_water, surface=surface)

    if r is not None:
        if len(r) == 2:
            density_dist.run(start=r[0], stop=r[1])
        elif len(r) == 3:
            density_dist.run(start=r[0], stop=r[1], step=r[2])
    else:
        density_dist.run()


if __name__ == '__main__':
    main()
