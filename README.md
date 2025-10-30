# mdkits
[中文文档](README_zh.md)

`mdkits` provides a variety of tools. Installation script:
```bash
pip install mdkits --upgrade
```

## General Option Parameter Types

1.  `CELL TYPE`: Specifies lattice cell parameters, e.g., `10,10,10`, `10,10,10,90,90,90`, etc.
2.  `FRAME RANGE`: Specifies the frame range, e.g., `1`, `1:10:2`, etc.
3.  `--group` and `--surface`: Select analysis objects using [selection language](https://userguide.mdanalysis.org/stable/selections.html).
4.  `--update_water`, `--distance`, and `--angle`: Enable dynamic update of water molecule positions during trajectory analysis.
5.  By specifying the `Host` in the corresponding `SSH config-file` on the server as the `ssh_name` environment variable, you can prepend `ssh_name` to the `path` in the script's output, which facilitates subsequent `scp` operations:
    ```bash
    ssh_name:path/to/file
    ```

## Trajectory File Processing Scripts

`md` is the trajectory file processing tool, which includes several processing utilities.

### Density Distribution

`density` is used to analyze the density distribution of a specific element along the z-axis in a system. For example, to analyze the density distribution of the `O` element along the z-axis:
```bash
mdkits md density [FILENAME] --group="name H" --cell [FILENAME]
```
This will output a file named `density_name_H.dat`, where the first column is the z-axis coordinate and the second column is the density distribution in units of mol/L. To output the density distribution in units of $g/cm^3$, you can specify the `--atomic_mass` option, for example:
```bash
mdkits md density [FILENAME] --group="name H" --cell [FILENAME] --atomic_mass=1.00784
```
This will output the density distribution in units of $g/cm^3$. You can specify surface atoms to normalize the density distribution to the surface, for example:
```bash
mdkits md density [FILENAME] --group="name O" --cell 10,10,10 --atomic_mass=18.01528 --surface="name Pt and name Ru"
```
This will normalize the density distribution to the surface and analyze the density distribution of water molecules using the positions of O atoms as the reference for water molecules. For systems with $OH^-$ ions, you can use the `--update_water` option to update the positions of water molecules in each frame, without needing to specify an element explicitly, for example:
```bash
mdkits md density [FILENAME] --update_water --cell 10,10,10 --atomic_mass=18.01528 --surface="name Pt and name Ru"
```
The output file will be named `density_water.dat`.

### Hydrogen Bonds

`hb` is used to analyze hydrogen bonds in a system, for example, to analyze the distribution of hydrogen bonds along the z-axis:
```bash
mdkits md hb [FILENAME] --cell 10,10,40 --surface "prop z < 10" --update_water
```
Or to analyze hydrogen bonds of a single water molecule:
```bash
mdkits md hb [FILENAME] --cell 10,10,40 --index 15
```

### Angle

`angle` is used to analyze the abundance distribution of the angle between the bisector vector of a water molecule's OH bond and the surface normal. For example, to analyze the angle abundance distribution of water molecules within 5 Å of the surface:
```bash
mdkits md angle [FILENAME] --cell 10,10,40 --surface "name Pt" --water_height 5
```

### Dipole Distribution

`diople` is used to analyze the dipole ($\cos \phi \rho_{H_2 O}$) distribution in a system. For example, to analyze the $\cos \phi \rho_{H_2 O}$ distribution in the system:
```bash
mdkits md diople [FILENAME] --cell 10,10,40 --surface "name Pt"
```

### Radial Distribution Function (RDF)

`rdf` is used to analyze the radial distribution function between two `group`s. For example, to analyze the radial distribution function between `O` and `H` elements in the system:
```bash
mdkits md rdf [FILENAME] --group "name O" "name H" --cell 10,10,40 --range 0.1 5
```

### Mean Squared Displacement (MSD)

`msd` is used to analyze the mean squared displacement of certain atoms in a system. For example, to analyze the MSD of `Li` atoms along the z-axis:
```bash
mdkits md msd [FILENAME] z "name Li"
```

### Monitor

`monitor` is used to monitor changes in atom height, bond length, and bond angle in a system. For example, to monitor the height of the atom with `index` 0:
```bash
mdkits md monitor [FILENAME] --cell 10,10,40 --surface "name Pt" -i 0
```
This will output the height from the surface as a function of each frame. To monitor the bond length between atoms 0 and 1:
```bash
mdkits md monitor [FILENAME] --cell 10,10,40 --surface "name Pt" -i 0 -i 1
```
This will output the heights from the surface for atoms 0 and 1, and the bond length between 0 and 1 as a function of each frame. To monitor the bond angle of 1-0-2:
```bash
mdkits md monitor [FILENAME] --cell 10,10,40 --surface "name Pt" -i 1 -i 0 -i 2
```
This will output the heights from the surface for atoms 1, 0, and 2, the bond lengths between 1-0 and 0-2, and the bond angle 1-0-2 as a function of each frame. Note that atoms at the vertex of an angle should be placed in the middle.

### Position Normalization

`wrap` is used to normalize the atomic positions in a trajectory file. For example, to normalize the atomic positions in `[FILENAME]` within the unit cell and output it as `wrapped.xyz`. By default, it reads `ABC` and `ALPHA_BETA_GAMMA` information from the `cp2k` output file `input_inp` as lattice cell parameters:
```bash
mdkits md wrap [FILENAME]
```
Or specify the `cp2k` input file:
```bash
mdkits md wrap [FILENAME] --cp2k_input_file setting.inp
```
Or specify the lattice cell parameters:
```bash
mdkits md wrap [FILENAME] --cell 10,10,10
```
The default `[FILENAME]` is `*-pos-1.xyz`.

### Vibrational Density of States (VDOS)

`vac` is used to analyze the velocity autocorrelation function of a trajectory and compute the Fourier transform of the velocity autocorrelation function, which is the vibrational density of states (VDOS). For example, to analyze the VDOS of the system:
```bash
mdkits md vac h2o-vel-1.xyz
```
The default `[FILENAME]` is `*-vel-1.xyz`.

## DFT Property Analysis Scripts

`dft` is the DFT property analysis tool, which includes several analysis utilities.

### PDOS

`pdos` is used to analyze the PDOS of a system. To analyze the d-orbital DOS of `[FILENAME]`:
```bash
mdkits dft pdos [FILENAME] -t d
```

### CUBE Files

`cube` is used to process files in [`cube` format](https://paulbourke.net/dataformats/cube/), averaging them along the z-axis:
```bash
mdkits dft cube [FILENAME]
```
The processed data will be output to `cube.out`. You can also calculate the average value within a specific region:
```bash
mdkits dft cube [FILENAME] -b 1 2
```
This will print the average value to the screen and also record it in the comment line of `cube.out`.

## Modeling

`build` is the modeling tool, which includes several modeling utilities.

### Building Bulk Models

`bulk` is used to build bulk models. For example, to build an `fcc` bulk model of `Pt`:
```bash
mdkits build bulk Pt fcc
```
To build as a conventional cell model:
```bash
mdkits build bulk Pt fcc --cubic
```
To build a `Caesium chloride` structure model:
```bash
mdkits build bulk CsCl cesiumchloride -a 4.123
```
To build a `fluorite` structure model:
```bash
mdkits build bulk BaF2 fluorite -a 6.196
```

### Building Surface Models

`surface` is used to build common surface models. Usage:
```bash
mdkits build surface [ELEMENT] [SURFACE_TYPE] [SIZE]
```
For example, to build an `fcc111` surface model of `Pt`:
```bash
mdkits build surface Pt fcc111 2 2 3 --vacuum 15
```
To build a graphene surface:
```bash
mdkits build surface C2 graphene 3 3 1 --vacuum 15
```

### Building Surface Models from Existing Structures

`cut` is used to build surface models from existing structures (the structure must be in a conventional cell). For example, to build an `fcc331` surface model from `Pt_fcc.cif`:
```bash
mdkits build cut Pt_fcc.cif --face 3 3 1 --size 3 3 5 --vacuum 15
```

### Adding Adsorbates to Surface Structures

`adsorbate` is used to add adsorbates to surface structures. For example, to add an `H` atom to `surface.cif`:
```bash
mdkits build adsorbate surface.cif H --select "index 0" --height 1    
```
Or to add an `H` atom with a coverage of 5 to `Pt_fcc111_335.cif`:
```bash
mdkits build adsorbate Pt_fcc111_335.cif H --select "prop z > 16" --height 2 --cover 5
```

### Building Solution Phase Models

`solution` is used to build solution phase models. When using for the first time, you should install `juliaup`:
```bash
mdkits build solution --install_julia
```
Then install `Packmol`:
```bash
mdkits build solution --install_packmol
```
After successful installation, you can use the `solution` functionality. For example, to build a water box with 32 water molecules:
```bash
mdkits build solution --water_number 32 --cell 9.86,9.86,9.86
```
Or to build a solution containing ions:
```bash
mdkits build solution li.xyz k.xyz --water_number 64 --tolerance 2.5 -n 25 -n 45 --cell 15,15,15
```
Here, the number of `-n` arguments must match the number of specified solvent molecule types, used to specify the number of solvents to add, respectively. Alternatively, build a solution phase model from `packmol` input files:
```bash
mdkits build solution input.pm input2.pm  --infile
```

### Building Interface Models

`interface` is used to build interface models. For example, to build an interface model without vacuum:
```bash
mdkits build interface --slab Pt_fcc100_555.cif --sol water_160.cif
```
Or to build an interface with a gas phase model:
```bash
mdkits build interface --slab Pt_fcc100_555.cif --sol water_160.cif --cap ne --vacuum 20
```

### Building Supercell Models

`supercell` is used to build supercell models:
```bash
mdkits build supercell Li3PO4.cif 2 2 2
```

## Others

### Trajectory Extraction

`extract` is used to extract specific frames from a trajectory file. For example, to extract frames from the 1000th to the 2000th frame from `frames.xyz` and output them to `1000-2000.xyz`. The parameters for the `-r` option are consistent with Python's slicing syntax:
```bash
mdkits extract frames.xyz -r 1000:2000 -o 1000-2000.xyz
```
Or to extract the last frame from the default trajectory file `*-pos-1.xyz` generated by `cp2k` and output it as `frames_-1.xyz` (which is the default behavior of `extract`):
```bash
mdkits extract
```
Or to output a structure every 50 frames into the `./coord` directory, while adjusting the output format to `cp2k`'s `@INCLUDE coord.xyz` format:
```bash
mdkits extract -cr ::50
```
To extract the positions of specific elements, for example, to extract the positions of `O` and `H` elements:
```bash
mdkits extract --select "name O or name H"
```

### Structure File Conversion

`convert` is used to convert structure files from one format to another. For example, to convert `structure.xyz` to `out.cif` (default filename is `out`). For files that do not store periodic boundary conditions, you can use the `--cell` option to specify `PBC`:
```bash
mdkits convert -c structure.xyz --cell 10,10,10
```
To convert `structure.cif` to `POSCAR`:
```bash
mdkits convert -v structure.cif
```
To convert `structure.cif` to `structure_xyz.xyz`:
```bash
mdkits convert -c structure.cif -o structure_xyz
```

### Data Processing

`data` is used for data processing, such as:
1.  `--nor`: Normalizes the data.
2.  `--gaus`: Applies Gaussian filtering to the data.
3.  `--fold`: Folds and averages stacked data.
4.  `--err`: Calculates error bars for the data.
And so on.

### Plotting Tool

`plot` is used for plotting data. `plot` requires reading a YAML format configuration file for plotting. The YAML file format is as follows:
```yaml
# plot mode 1
figure1:
  data:
    legend1: ./data1.dat
    legend2: ./data2.dat
  x:
    0: x-axis
  y:
    1: y-axis
  x_range: 
    - 5
    - 15

# plot mode 2
figure2:
  data:
    y-xais: ./data.dat
  x:
    0: x-axis
  y:
    1: legend1
    2: legend2
    3: legend3
    4: legend4
    5: legend5
  y_range:
    - 0.5
    - 6
  legend_fontsize: 12

# plot mode error
12_dp_e_error:
  data:
    legend: ./error.dat
  x:
    0: x-axis
  y:
    1: y-axis
  fold: dp
  legend_fontsize: 12
```
The above illustrates three plotting modes supported by `plot`: `mode 1`, `mode 2`, and `mode error`. `mode 1` is used for comparing the same column data from multiple data files, `mode 2` is used for comparing different column data from the same data file, and `mode error` is used for plotting mean squared error plots.

`plot` can process multiple YAML files simultaneously. Each YAML file can contain multiple plotting configurations. Plotting configurations for `mode 1` and `mode 2` can be automatically recognized, but the `error` mode requires explicit specification, for example:
```bash
mdkits plot *.yaml
```
and:
```bash
mdkits plot *.yaml --error
```