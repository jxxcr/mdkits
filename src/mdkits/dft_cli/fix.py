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
    atoms = Universe(filename).select_atoms(group)
    indices = atoms.indices + 1
    # 将 indices 转换为字符串：连续区间用 "start..end"，不连续索引用空格分隔
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
        # 处理最后一段
        if start == prev:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}..{prev}")
        list_str ="LIST " + " ".join(ranges)

    print(list_str)
    with open(o, 'w') as f:
        f.write(list_str + '\n')