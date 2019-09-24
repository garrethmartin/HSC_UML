__author__ = 'ah14aeb'

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import normalisation

def plot_pca_eigenvectors(components_, num_components):
    gs1 = gridspec.GridSpec(num_components, 1)
    fig = plt.figure()
    width = 1
    for i in range(num_components):
        ax = fig.add_subplot(gs1[i])
        ind = np.arange(components_[i].shape[0])
        rects1 = ax.bar(ind, components_[i], width, color='r')
        ax.set_xlabel("")
        ax.set_xticks(ind+width)
        ax.set_ylabel("")
        ax.grid(True)
        ax.set_title("PC {0} Values".format(i+1))
    plt.show()


def plot_scatter(pca_data, principle_comps, title="PCA", output_folder_path=None, show_plot=True):
    gs1 = gridspec.GridSpec(1, 1)
    fig = plt.figure()
    ax1 = fig.add_subplot(gs1[0], projection='3d')
    ax1.scatter(pca_data[:, principle_comps[0]], pca_data[:, principle_comps[1]], zs=pca_data[:, principle_comps[2]], s=1, picker=True)
    ax1.set_xlabel("Principle Component {0}".format(principle_comps[0] + 1))
    ax1.set_ylabel("Principle Component {0}".format(principle_comps[1] + 1))
    ax1.set_zlabel("Principle Component {0}".format(principle_comps[2] + 1))
    ax1.set_title(title)
    if output_folder_path != None:
        plt.savefig(output_folder_path)
    if show_plot:
        plt.show()

def pca_and_plot(output_folder_path, samples, plot_eigen_vectors=False, show_plot=True):

    U, S, V = normalisation.native_pca(samples)
    components_ = V
    pca_astro_data = normalisation.native_transform(samples, components_, 3)

    if plot_eigen_vectors:
        plot_pca_eigenvectors(components_, 3)

    principle_components_3d = np.array([0, 1, 2])
    plot_scatter(pca_astro_data, principle_components_3d, "PCA", output_folder_path, show_plot=show_plot)