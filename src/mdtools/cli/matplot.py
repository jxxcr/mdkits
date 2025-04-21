#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
from matplotlib import use as muse
muse('Agg')


def parse_slice(s):
    if s == None:
        return None
    return [int(x) for x in s.replace(':', ' ').split()]


def parse_argument():
    parser = argparse.ArgumentParser(description='extract pos file from output file')

    parser.add_argument('input_file_name', type=str, help='input file name')
    parser.add_argument('-o', type=str, help='output file name, default is "out.xyz"', default='out.png')
    parser.add_argument('-u', type=parse_slice, help='which clume to use, look like gnuplot u 1:2', default=[0, 1])
    parser.add_argument('--label', type=str, help='line name')
    parser.add_argument('--dpi', type=int, help='image dpi, default is 300', default=300)
    parser.add_argument('--err',  help='plot err line', action='store_true')

    return parser.parse_args()


def plot_data(x, y, dpi, label, name):
    fig, ax = plt.subplots(dpi=dpi)
    ax.plot(x, y, label=label)
    ax.legend()
    fig.savefig(name)


def plot_err(x, y, dpi, label, name):
    fig, ax = plt.subplots(dpi=dpi)
    ax.scatter(x, y, label=label)
    line = np.linspace(np.amax(x), np.amin(x), 1000)
    ax.plot(line, line)
    ax.legend()
    fig.savefig(name)


def main():
    args = parse_argument()
    if args.label == None:
        args.label = args.input_file_name
    data = np.loadtxt(args.input_file_name)
    if args.err:
        plot_err(data[:, 0], data[:, 1], dpi=args.dpi, label=args.label, name=args.o)
    else:
        plot_data(data[:, 0], data[:, 1], dpi=args.dpi, label=args.label, name=args.o)

    print(os.path.abspath(args.o))


if __name__ == '__main__':
    main()
