import click, os
from mdkits.util import arg_type
from importlib import resources
from mdkits.cli import convert
import tempfile, platform, subprocess, sys


@click.command(name="solution")
@click.argument("filename", type=click.Path(exists=True), nargs=-1)
@click.option('--infile', is_flag=True, help="read input mode")
@click.option('--install_julia', is_flag=True, help="install julia for system")
@click.option('--install_packmol', is_flag=True, help="init julia install packmol")
@click.option('--water_number', type=int, help="number of water molecules", default=0, show_default=True)
@click.option('-n', type=int, multiple=True, help="number of molecules")
@click.option('--tolerance', type=float, help="tolerance of solution", default=3.5, show_default=True)
@click.option('--cell', type=arg_type.Cell, help="set cell, a list of lattice: --cell x,y,z or x,y,z,a,b,c")
@click.option('--gap', type=float, help="gap between solution and cell", default=1, show_default=True)
def main(filename, infile, install_julia, install_packmol, water_number, n, tolerance, cell, gap):
    """
    build solution model
    """
    os_name = platform.system()

    if install_julia:
        if os_name in ("Darwin", "Linux", "FreeBSD"):
            try:
                subprocess.run(
                ["curl -fsSL https://install.julialang.org | sh"],
                shell=True,  
                check=True,
            )
                print("Julia installed (macOS, Linux, FreeBSD).")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"Julia install failed: {e}")
                sys.exit(0)
        elif os_name == "Windows":
            try:
                subprocess.run(
                    ["winget", "install", "--name", "Julia", "--id", "9NJNWW8PVKMN", "-e", "-s", "msstore"],
                    check=True,
                )
                print("Julia installed (Windows).")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"Julia install failed: {e}")
                sys.exit(0)
        else:
            print(f"unsupport os: {os_name}")
            sys.exit(0)

    if install_packmol:
        import julia
        julia.install()

        from julia.api import Julia
        jl = Julia(compiled_modules=False)

        from julia import Pkg, Main
        Pkg.add("PyCall")
        Pkg.activate("Packmol", shared=True)
        Pkg.add("Packmol")
        Main.exit()
    else:
        if os_name in ("Darwin", "Linux"):
            from julia.api import Julia
            jl = Julia(compiled_modules=False)

        from julia import Pkg, Main

        if cell is None:
            raise ValueError("cell should be provided")

        if len(filename) == 0 and water_number == 0:
            raise ValueError("at least one file should be provided, or water_number should be greater than 0")

        if os_name in ("Darwin", "Linux"):
            Pkg.activate("Packmol", shared=True)

        while True:
            try:
                Main.using("Packmol")
                break
            except Exception:
                pass

        if infile:
            for file in filename:
                Main.run_packmol(file)
        else:
            if len(n) != len(filename):
                raise ValueError("number of -n should be equal to number of files")

            temp_file = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
            backslash = "\\"

            structure_input = {}
            output_filenames = []
            if len(filename) > 0:
                for index, file in enumerate(filename):
                    structure_input[file] = f"structure {os.path.join(os.getcwd(), file.replace(backslash, '/').replace('./', ''))}\n  number {n[index]}\n  inside box {gap} {gap} {gap} {cell[0]-gap} {cell[1]-gap} {cell[2]-gap}\nend structure\n"

                    output_filenames.append(f"{file.replace(backslash, '/').split('.')[-2].split('/')[-1]}_{n[index]}")

            if water_number > 0:
                water_path = resources.files('mdkits.build_cli').joinpath('water.xyz')

                structure_input["water"] = f"structure {water_path}\n  number {water_number}\n  inside box {gap} {gap} {gap} {cell[0]-gap} {cell[1]-gap} {cell[2]-gap}\nend structure\n"

                output_filenames.append(f"{str(water_path).replace(backslash, '/').split('.')[-2].split('/')[-1]}_{water_number}")

            output_filename = "-".join(output_filenames) + ".xyz"
            head_input = f"tolerance {tolerance}\nfiletype xyz\noutput {os.path.join(os.getcwd(), output_filename)}\npbc {cell[0]} {cell[1]} {cell[2]}\n"

            total_input = head_input + "\n".join(structure_input.values())
    
            temp_file.write(total_input)
            temp_file.flush()
            temp_file.close()

            Main.run_packmol(temp_file.name)

            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

        print("="*15)
        print(total_input)
        print("="*15)
        convert.main([output_filename, "-c", "--cell", ",".join([str(a) for a in cell])], standalone_mode=False)
        Main.exit()


if __name__ == "__main__":
    main()