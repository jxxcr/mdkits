#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
import matplotlib.ticker as ticker
import yaml, click
from mdkits.util import fig_operation

DEFAULT_CONFIG = {
        'data': {},
        'x': {},
        'y': {},
        'figsize': None,
        'x_range': None,
        'y_range': None,
        'legend_fontsize': None,
        'ticks_fontsize': None,
        'line': {},
        'fold': None
    }


def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"no file {file_path}")
        exit(1)
    except yaml.YAMLError as exc:
        print(f"yaml parse error: {exc}")
        exit(1)
    config = data.copy()
    #for key, default in DEFAULT_CONFIG.items():
    #    config[key] = data.get(key, default)
    for key, value in config.items():
        for dkey, dvalue in DEFAULT_CONFIG.items():
            value[dkey] = data[key].get(dkey, dvalue)

    return config


def check_figsize(figsize):
    match figsize:
        case list() if len(figsize) == 2:
            rcParams['figure.figsize'] = figsize
        case None:
            pass
        case _:
            print("wrong yaml structure")
            exit(1)


def check_int_ticks(ax, int_ticks):
    match int_ticks:
        case 'x':
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        case 'y':
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        case 'a':
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        case _:
            pass


def check_axis_range(ax, x_range=None, y_range=None):
    if x_range:
        match x_range:
            case list() if len(x_range) == 2:
                ax.set_xlim(x_range[0], x_range[1])
            case None:
                pass
            case _:
                print("wrong yaml structure")
                exit(1)
    if y_range:
        match y_range:
            case list() if len(y_range) == 2:
                ax.set_ylim(y_range[0], y_range[1])
            case None:
                pass
            case _:
                print("wrong yaml structure")
                exit(1)


def check_lenend_fontsize(ax, legend_fontsize, rmse=None):
    if rmse is not None:
        match legend_fontsize:
            case int():
                l = ax.legend(fontsize=legend_fontsize, markerscale=0, handlelength=0)
            case None:
                l = ax.legend(markerscale=0, handlelength=0)
            case _:
                pass

        #p = l.get_window_extent()
        #ax.annotate(f"RMSE:{rmse:.4f}", (p.p0[0], p.p1[1]), (p.p0[0], p.p1[1]-300), xycoords='figure pixels', fontsize=legend_fontsize)
    else:
        match legend_fontsize:
            case int():
                ax.legend(fontsize=legend_fontsize)
            case None:
                ax.legend()
            case _:
                pass


def check_output_mode(fig, plt, m, figure, fold=None):
    match m:
        case 'show':
            plt.show()
        case 'save':
            fig_operation.savefig(fig, f"{figure}", fold)
            plt.close()
        case 'all':
            fig_operation.savefig(fig, f"{figure}", fold)
            plt.show()
            plt.close()
        case _:
            pass


def check_ticks_fontsize(ax, ticks_fontsize):
    match ticks_fontsize:
        case int():
            ax.tick_params(axis='both', labelsize=ticks_fontsize)
        case None:
            pass
        case _:
            pass


def mode_1(data_dict, figure, **kwargs):
    # init config
    check_figsize(data_dict['figsize'])

    fig, ax = plt.subplots()

    # ticks config
    check_int_ticks(ax, kwargs['int_ticks'])

    # plot part
    for label, data in data_dict['data'].items():
        label = r"$\mathrm{ "+ label +" }$"
        data = np.loadtxt(data)
        x_slice, xlabel = next(iter(data_dict['x'].items()))
        for y_slice, ylabel in data_dict['y'].items():
            ax.plot(data[:, x_slice], data[:, y_slice], label=label)

        # range config
        check_axis_range(ax, x_range=data_dict['x_range'], y_range=data_dict['y_range'])

        # axis label part
        ax.set_xlabel(r"$\mathrm{ "+ xlabel +" }$")
        ax.set_ylabel(r"$\mathrm{ "+ ylabel +" }$")

        # h or v line
        match data_dict['line']:
            case _:
                pass

        # legend config
        check_lenend_fontsize(ax, data_dict['legend_fontsize'])

    # output part
    check_output_mode(fig, plt, kwargs['m'], figure, data_dict['fold'])


def mode_2(data_dict, figure, **kwargs):
    # init config
    check_figsize(data_dict['figsize'])

    fig, ax = plt.subplots()

    # ticks config
    check_int_ticks(ax, kwargs['int_ticks'])

    # plot part
    ylabel, data = next(iter(data_dict['data'].items()))
    data = np.loadtxt(data)
    x_slice, xlabel = next(iter(data_dict['x'].items()))
    for y_slice, label in data_dict['y'].items():
        label = r"$\mathrm{ "+ label +" }$"
        ax.plot(data[:, x_slice], data[:, y_slice], label=label)

        # range config
        check_axis_range(ax, x_range=data_dict['x_range'], y_range=data_dict['y_range'])

        # axis label part
        ax.set_xlabel(r"$\mathrm{ "+ xlabel +" }$")
        ax.set_ylabel(r"$\mathrm{ "+ ylabel +" }$")

    # legend config
    check_lenend_fontsize(ax, data_dict['legend_fontsize'])

    # output part
    check_output_mode(fig, plt, kwargs['m'], figure, data_dict['fold'])


def mode_error(data_dict, figure, **kwargs):
    # init config
    check_figsize(data_dict['figsize'])

    fig, ax = plt.subplots(figsize=(4.8, 4.8))

    # ticks config
    check_int_ticks(ax, kwargs['int_ticks'])

    # plot part
    label, data = next(iter(data_dict['data'].items()))
    data = np.loadtxt(data)
    x_slice, xlabel = next(iter(data_dict['x'].items()))
    for y_slice, ylabel in data_dict['y'].items():
        label = r"$\mathrm{ "+ label +" }$"
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        ax.scatter(data[:, x_slice], data[:, y_slice], label=label)
        data_diff = data[:, x_slice] - data[:, y_slice]
        data_rmse = np.sqrt(np.average(data_diff*data_diff))
        ax.axline((data[0, x_slice], data[0, x_slice]), slope=1, ls='--', c='black')
        ax.set_xticks([])
        ax.set_yticks([])
        check_lenend_fontsize(ax, data_dict['ticks_fontsize'])

        # range config
        check_axis_range(ax, x_range=data_dict['x_range'], y_range=data_dict['y_range'])

        # axis label part
        ax.set_xlabel(r"$\mathrm{ "+ xlabel +" }$")
        ax.set_ylabel(r"$\mathrm{ "+ ylabel +" }$")

        lims = [np.min([ax.get_xlim(), ax.get_ylim()]), np.max([ax.get_xlim(), ax.get_ylim()])]
        ax.text(lims[0]+(lims[1]-lims[0])*.6, lims[0]+(lims[1]-lims[0])*.1, f"RMSE: {data_rmse:.4f}", fontsize=data_dict['legend_fontsize'])
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        #ax.set_aspect('equal')
    #plt.axis('equal')
    # legend config
    check_lenend_fontsize(ax, data_dict['legend_fontsize'], rmse=data_rmse)

    # output part
    check_output_mode(fig, plt, kwargs['m'], figure, data_dict['fold'])


@click.command(name='plot')
@click.argument('yaml_file', type=click.Path(exists=True), nargs=-1)
@click.option('--int_ticks', help='set x ticks or y ticks with int, choices: x, y, a(all)', type=click.Choice(['x', 'y', 'a']))
@click.option('--error', help='set error mode', is_flag=True)
@click.option('-m', help='output mode: show, save, all, default is save', type=click.Choice(['show', 'save', 'all']), default='save')
def main(yaml_file, int_ticks, error, m):
    """
    a plot tool, read yaml file to plot
    """

    kwargs = locals()
    figure_dict = {}
    for yaml_file in yaml_file:
        yaml_dict = load_config(yaml_file)
        figure_dict.update(yaml_dict)

        for figure, data_dict in figure_dict.items():
            check_data = len(data_dict['data'])

            # mode error
            if error:
                mode = 'error'
                mode_error(data_dict, figure, **kwargs)

            # mode 1
            elif check_data > 1:
                if len(data_dict['y']) > 1:
                    print("wrong yaml structure")
                    exit(1)
                mode = 1
                mode_1(data_dict, figure, **kwargs)

            # mode 2
            elif check_data == 1:
                mode = 2
                mode_2(data_dict, figure, **kwargs)

            else:
                print("wrong yaml structure")
                exit(1)
            print(f"{figure} is done with mode {mode}")


if __name__ == '__main__':
    main()
