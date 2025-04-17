#!/usr/bin/env python3

import numpy as np
import click
import os, glob


def match_file(patch):
    pwd = os.getcwd()
    match_file = glob.glob(os.path.join(pwd, patch))

    return match_file


@click.command(name='data')
@click.argument('filename', nargs=-1, type=click.Path(exists=True))
@click.option('--nor', help='normalized data', is_flag=True)
@click.option('--gaus', type=int, help='gaussian filter 1d data', default=0)
@click.option('--fold', help='fold and average', is_flag=True)
@click.option('--err', help='error bar of data', is_flag=True)
@click.option('--int_cn', type=float, nargs=2, help='integrate gofr data to coordination number', default=None)
def main(filename, nor, gaus, fold, err, int_cn):
    """
    trade data file with different method
    """

    for data_file in filename:
        data = np.loadtxt(data_file)
        data_name = data_file.split(os.sep)[-1]
        if len(data.shape) == 1:
            data = np.hstack((np.arange(data.shape[0]).reshape(-1, 1), data.reshape(-1, 1)))
        data_range = data.shape[1]
        if nor:
            nor_data = data.copy()
            for i in range(1, data_range):
                nor_data[:, i] = data[:, i] / np.max(data[:, i])
            np.savetxt(f'./nor_{data_name}', nor_data, fmt='%.2e', delimiter='\t')
        elif gaus > 0:
            from scipy.ndimage import gaussian_filter1d
            gaus_data = data.copy()
            for i in range(1, data_range):
                gaus_data[:, i] = gaussian_filter1d(data[:, i], gaus)
            np.savetxt(f"./gaus_{data_name}", gaus_data, fmt='%.2e', delimiter='\t')
        elif fold:
            data_shape = data.shape
            mid = int(data_shape[0] // 2)
            left_data = data[:mid, 1:]
            right_data = data[mid:, 1:][::-1]
            if data_shape[0] % 2 != 0:
                left_data = np.vstack((left_data, right_data[-1]))
                mid += 1
            fold_data = (left_data + right_data) / 2
            fold_data = np.hstack((data[:mid, 0].reshape(-1, 1), fold_data))
            np.savetxt(f"./fold_{data_name}", fold_data, fmt='%.2e', delimiter='\t')
        elif err:
            err_data = data.copy()
            std_dev_list = []
            for i in range(1, data_range):
                split_array = np.array_split(err_data[:, i], 5)
                averages = np.array([np.mean(part) for part in split_array])
                std_dev = averages.std(axis=0)
                std_dev_list.append(std_dev)
            np.savetxt(f"./error_{data_name}", np.vstack(std_dev_list), fmt='%.5f', delimiter='\t')
        elif int_cn is not None:
            from scipy import integrate
            rho = 32/(9.86**3)
            x = data[:, 0]
            mask = (x >= int_cn[0]) & (x <= int_cn[1])
            filtered_x = x[mask]
            filtered_y = data[:, 1][mask]
            integrate_y = 4 * np.pi * rho * np.insert(integrate.cumulative_trapezoid(filtered_y*filtered_x**2, filtered_x), 0, 0)
            np.savetxt(f"int_cn_{data_name}", np.hstack((filtered_x.reshape(-1, 1), integrate_y.reshape(-1, 1))), fmt='%.5f', delimiter='\t')



        print(f"================ processing of {data_name} is done ===================")


if __name__ == '__main__':
    main()
