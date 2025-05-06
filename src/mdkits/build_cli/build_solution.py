import click, io
from julia import Pkg, Main
from mdkits.util import arg_type
from importlib import resources



@click.command(name="solution")
@click.argument("filename", type=click.Path(exists=True), nargs=-1)
@click.option('--water_number', type=int, help="number of water molecules", default=0, show_default=True)
@click.option('-n', type=int, multiple=True, help="number of molecules")
@click.option('--tolerance', type=float, help="tolerance of solution", default=3.5, show_default=True)
@click.option('--cell', type=arg_type.Cell, help="set cell, a list of lattice: --cell x,y,z or x,y,z,a,b,c")
@click.option('--gap', type=float, help="gap between solution and cell", default=1, show_default=True)
def main(filename, water_number, n, tolerance, cell, gap):
    Pkg.activate("Packmol", shared=True)
    Pkg.add("Packmol")

    while True:
        try:
            Main.using("Packmol")
            break
        except Exception:
            pass

    backslash = "\\"

    structure_input = {}
    output_filename = ''
    for index, file in enumerate(filename):
        structure_input[file] = f"structure {file}\n  number {n[index]}\n  inside box {cell[0]+gap} {cell[1]+gap} {cell[2]+gap} {cell[0]-gap} {cell[1]-gap} {cell[2]-gap}\nend structure\n"

        output_filename += f"{file.replace(backslash, '/').split('.')[-2].split('/')[-1]}_{[index]}_"

    if water_number > 0:
        water_path = resources.files('mdkits.build_cli').joinpath('water.xyz')

        structure_input["water"] = f"structure {water_path}\n  number {water_number}\n  inside box {cell[0]+gap} {cell[1]+gap} {cell[2]+gap} {cell[0]-gap} {cell[1]-gap} {cell[2]-gap}\nend structure\n"

        output_filename += f"{str(water_path).replace(backslash, '/').split('.')[-2].split('/')[-1]}_{water_number}_"

    head_input = f"tolerance {tolerance}\nfiletype xyz\noutput {output_filename}.xyz\npbc {cell[3]} {cell[4]} {cell[5]}\n"

    total_input = head_input + "\n".join(structure_input.values())
    
    virtual_file = io.StringIO()
    virtual_file.write(total_input)

    Main.run_packmol(virtual_file)
    Main.exit()


if __name__ == "__main__":
    main()