import argparse


def parse_cell(s):
    return [float(x) for x in s.replace(',', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description='generate packmol input file with give parameter')
    parser.add_argument('--size', type=int, help='water size default is 30', default=30)
    parser.add_argument('--cell', type=parse_cell, help='input box size(a,b,c)')
    parser.add_argument('--addwat', type=int, help='add some additional water, default is 0', default=0)
    parser.add_argument('--ioncon', type=float, help='concentration of sol box, default is 0.0', default=0.0)
    parser.add_argument('--tolerance', type=float, help='tolerance of packmol, default is 2.5', default=2.5)
    parser.add_argument('--watpath', type=str, help='water xyz file path', default='C:\\home\\.can\\temp\\packmol\\default\\water.xyz')
    parser.add_argument('--ionpath', type=str, help='ion xyz file path')
    parser.add_argument('-o', type=str, help='output file name, default is "input.pm"', default='input.pm')
    parser.add_argument('--output', type=str, help='output file name of packmol, default is "solbox.xyz"', default='solbox.xyz')

    return parser.parse_args()


def get_water_number():
    water_number = water_volume / water_size

    return int(round(water_number, 0))


def get_ion_number(concentration):
    ion_number = ( (concentration * avogadro) / 1e+27 ) * water_volume

    return int(round(ion_number, 0))


def main():
    global water_volume, water_size, avogadro
    args = parse_argument()
    water_volume = args.cell[0] * args.cell[1] * args.cell[2]
    water_size = args.size
    avogadro = 6.02214179e+23
    water_number = get_water_number() + args.addwat
    ion_number = get_ion_number(args.ioncon)

    if ion_number == 0:
        packmol_input_str = f"""
        tolerance {args.tolerance}
        filetype xyz
        output {args.output}
        pbc {args.cell[3]} {args.cell[4]} {args.cell[5]}
        structure {args.watpath}
          number {water_number}
          inside box 2. 2. 2. {args.cell[0]-2} {args.cell[1]-2} {args.cell[2]-2}
        end structure
        """
    else:
        packmol_input_str = f"""
        tolerance {args.tolerance}
        filetype xyz
        output {args.output}
        pbc {args.cell[3]} {args.cell[4]} {args.cell[5]}
        structure {args.watpath}
          number {water_number}
          inside box 2. 2. 2. {args.cell[0]-2} {args.cell[1]-2} {args.cell[2]-2}
        end structure
        structure {args.ionpath}
          number {ion_number}
          inside box 2. 2. 2. {args.cell[0]-2} {args.cell[1]-2} {args.cell[2]-2}
        end structure
        """

    with open(args.o, 'w') as f:
        f.write(packmol_input_str)


if __name__ == '__main__':
    main()
