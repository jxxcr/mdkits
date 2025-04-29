import os, shutil, atexit


def make_temp_dir(temp_dir, delete=False):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    if delete:
        atexit.register(remove_temp_dir, temp_dir)


def remove_temp_dir(temp_dir):
    shutil.rmtree(temp_dir)


def default_file_name(match, last=False):
    import glob
    file_list = glob.glob(match)
    if file_list:
        if last:
            default_file_name = sort_word_and_number(file_list)[-1]
        else:
            default_file_name = list(file_list)
    else:
        default_file_name = None

    return default_file_name


def sort_word_and_number(unsort_list):
    import re
    fns = lambda s: sum(((s,int(n))for s,n in re.findall('(\D+)(\d+)','a%s0'%s)),())
    sorted_list = sorted(unsort_list, key=fns)

    return sorted_list


def default_input():
    default_input_name = os.environ.get("DEFAULT_INPUT", "input.inp,setup.inp,cell.inc").split(',')
    return default_input_name