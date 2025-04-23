#!/usr/bin/env python3

import numpy as np
import click
from MDAnalysis import Universe
from MDAnalysis.analysis.base import AnalysisBase
from mdkits.util import (
    arg_type,
    numpy_geo,
    encapsulated_mda,
    os_operation,
)
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
            group = self.atomgroup.select_atoms(f"{self.element}")
            self._append(group.positions[:, 2])

        if self.surface_group:
            lower_z, upper_z = numpy_geo.find_surface(self.surface_group.positions[:, 2], layer_tolerance=1, surface_tolerance=5)
            self.surface_pos[0] += lower_z
            self.surface_pos[1] += upper_z

        self.frame_count += 1

    def _conclude(self):
        if self.frame_count > 0:
            V = self.u.dimensions[0] * self.u.dimensions[1] * self.bin_size

            if self.atomic_mass:
                density_distribution = (self.density_distribution * self.atomic_mass * 1.660539 / V) / self.frame_count
            else:
                density_distribution = (self.density_distribution * (10000/6.02) / V) / self.frame_count

            bins_z = np.arange(len(self.density_distribution)) * self.bin_size

            if self.surface:
                lower_z = self.surface_pos[0] / self.frame_count
                upper_z = self.surface_pos[1] / self.frame_count

                mask = (bins_z >= lower_z) & (bins_z <= upper_z)
                filtered_bins_z = bins_z[mask] - lower_z
                filtered_density_distribution = density_distribution[mask]

                conbined_data = np.column_stack((filtered_bins_z, filtered_density_distribution))
            else:
                conbined_data = np.column_stack((bins_z, density_distribution))

            np.savetxt(self.o, conbined_data, header="Z\tdensity", fmt='%.5f', delimiter='\t')

@click.command(name='density')
@click.argument('filename', type=click.Path(exists=True), default=os_operation.default_file_name('*-pos-1.xyz', last=True))
@click.option('--cell', type=arg_type.Cell, help='set cell from cp2k input file or a list of lattice: --cell x,y,z or x,y,z,a,b,c', default='input.inp', show_default=True)
@click.option('--element', type=str, help='element to analysis')
@click.option('--atomic_mass', type=float, help='output density unit (g/cm3), should give atomic mass of element, else is concentration unit (mol/L)')
@click.option('-o', type=str, help='output file name', default='density_{element}.dat', show_default=True)
@click.option('--update_water', is_flag=True, help='update water with distance or angle judgment')
@click.option('--distance', type=float, help='update water distance judgment', default=1.2, show_default=True)
@click.option('--angle', type=(float, float), help='update water angle judgment')
@click.option('--surface', type=str, help='surface element')
def main(filename, cell, o, element, atomic_mass, update_water, distance, angle, surface):
    """
    analysis density or concentration of element in a trajectory file
    """

    density_dist = Density_distribution(filename, cell, o=o, distance_judg=distance, angle_judg=angle, element=element, atomic_mass=atomic_mass, update_water=update_water, surface=surface)

    density_dist.run()


if __name__ == '__main__':
    main()
