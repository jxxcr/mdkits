import os
import matplotlib.pyplot as plt


def savefig(fig, name, fold=None):
    current_path = os.getcwd()
    if fold:
        if not os.path.exists(fold):
            os.mkdir(fold)
        fig.savefig(f"{current_path}/{fold}/{name}.png", format='png')
        vector_fig_dir = f'pdf'
        if not os.path.exists(vector_fig_dir):
            os.mkdir(vector_fig_dir)
        vector_fig_dir = f'pdf/{fold}'
        if not os.path.exists(vector_fig_dir):
            os.mkdir(vector_fig_dir)
        fig.savefig(f"{current_path}/{vector_fig_dir}/{name}.pdf", format='pdf', transparent=True)
    else:
        fig.savefig(f"{current_path}/{name}.png", format='png')
        vector_fig_dir = f'pdf'
        if not os.path.exists(vector_fig_dir):
            os.mkdir(vector_fig_dir)
        fig.savefig(f"{current_path}/{vector_fig_dir}/{name}.pdf", format='pdf', transparent=True)


def scaled_figsize(scale_w=1.0, scale_h=1.0):
    default_size = plt.rcParams["figure.figsize"]
    return [default_size[0]*scale_w, default_size[1]*scale_h]
