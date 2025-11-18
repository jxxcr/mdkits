import click
from MDAnalysis import Universe
from mdkits.util import encapsulated_ase, os_operation


@click.command(name='fix')
@click.argument('filename', type=click.Path(exists=True))
@click.argument('group', type=str)
@click.option('-o', type=str, help='output file name, default is "fix.inc"', default='fix.inc', show_default=True)
def main(filename, group, o):
    """
    generate fix.inc file for cp2k
    """
    
    with open(filename, 'r', encoding='utf-8') as fh:
        lines = fh.read().splitlines()
    first = lines[0].strip() if lines else ''
    if not first.isdigit():
        atoms_number = sum(1 for l in lines if l.strip())
        s = '\n'.join([str(atoms_number), ''] + lines) + '\n'
        import io
        virtual_file = io.StringIO(s)
        atoms = Universe(virtual_file, format='xyz').select_atoms(group)
    else:
        atoms = Universe(filename).select_atoms(group)
    indices = atoms.indices + 1
    fix_number = len(indices)
    fix_output = f"{fix_number} atoms have been fixed."
    
    arr = sorted(set(int(i) for i in indices))
    if not arr:
        list_str = ""
    else:
        ranges = []
        start = prev = arr[0]
        for x in arr[1:]:
            if x == prev + 1:
                prev = x
            else:
                if start == prev:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}..{prev}")
                start = prev = x
        
        if start == prev:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}..{prev}")
        list_str = "#" + fix_output + "\n" + "LIST " + " ".join(ranges)

    print(list_str)
    with open(o, 'w') as f:
        f.write(list_str + '\n')