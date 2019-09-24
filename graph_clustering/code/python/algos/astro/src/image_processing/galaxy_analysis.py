__author__ = 'AlexH'
import sys
import numpy as np
import config
import log
from astropy.io import fits as pyfits
from helpers import feature_helper
from helpers import normalisation as pcahelper
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import axes3d, Axes3D
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn import manifold

def plot_scatter_2d(orig, pca_data, principle_comps, labels, title="PCA", save_file=False, file_path=""):

    def onscatterpick(event):
        #thisline = event.artist
        index = event.ind
        print ('onpick points:{0} {1}'.format(index, orig[index, 0]))

    gs1 = gridspec.GridSpec(1, 1)
    fig = plt.figure()
    #ax1 = fig.add_subplot(gs1[0])
    ax1 = Axes3D(fig)
    #ax1 = fig.add_subplot(gs1[0], projection='3d')

    #ax1.scatter(pca_data[:, principle_comps[0]], pca_data[:, principle_comps[1]], s=5, picker=True)
    ax1.scatter(pca_data[:, principle_comps[0]], pca_data[:, principle_comps[1]], zs=pca_data[:, principle_comps[2]], s=3, color=labels, picker=True)

    ax1.set_xlabel("Principle Component {0}".format(principle_comps[0]))
    ax1.set_ylabel("Principle Component {0}".format(principle_comps[1]))
    ax1.set_zlabel("Principle Component {0}".format(principle_comps[2]))
    ax1.set_title(title)

    fig.canvas.mpl_connect('pick_event', onscatterpick)

    if save_file:
        fig.savefig(file_path)
        plt.close(fig)
    else:
        plt.show()

def normalize_rows(matrix):

    for i in range(matrix.shape[0]):
        total = np.sum(matrix[i, :])
        matrix[i, :] = matrix[i, :] / total
    return matrix

def main(config):

    counts_file_path = config['counts_file_path']
    gt_labels_file_path = config['labels']
    min_object_size_in_patches = int(config['min_patch_count'])

    logger.info("loading object counts file")
    counts = np.loadtxt(counts_file_path, dtype=np.int, delimiter=',')

    rows = counts.shape[0]
    cols = counts.shape[1] - 1

    logger.info("removing objects with num patches less than min_patch_count in config")
    min_patches = min_object_size_in_patches
    indices = []
    for i in range(rows):
        if np.sum(counts[i, 1:cols]) > min_patches:
            indices.append(i)
    indices = np.array(indices)

    large_counts = counts[indices, :]

    gt_labels = get_gt_labels(gt_labels_file_path, large_counts)

    logger.info("normalizing data")
    samples = large_counts[:, 1:]
    samples = samples.astype(np.float64)
    samples = normalize_rows(samples)

    logger.info("running pca")
    U, S, V = pcahelper.native_pca(samples)
    components_ = V
    vars = pcahelper.get_native_variance(S, samples.shape[0])
    pca_samples = pcahelper.native_transform(samples, components_, -1)

    principle_comps = np.array([1,2,3])

    logger.info("objects: {0}  large: {1}  min patches: {2}".format(rows, large_counts.shape[0], min_patches))

    plot_scatter_2d(large_counts, pca_samples, principle_comps, gt_labels) #gt_labels aggcolors


def get_colors(labels):
    cols = ['r','b','y','g','b','c']
    out_cols = []
    for i in range(len(labels)):
        out_cols.append(cols[labels[i]])
    return out_cols

def get_gt_labels(gt_labels_file_path, samples):
    gt_labels = np.loadtxt(gt_labels_file_path, dtype=np.int, delimiter=',')
    labels = []
    cols = ['b','r','y','g','m','c']
    for i in range(samples.shape[0]):
        objid = samples[i][0]
        lr = gt_labels[gt_labels[:, 0] == objid]
        if lr.shape[0] > 0:
            labels.append(cols[lr[0][1]])
        else:
            labels.append('k')
    return labels

# #######################################################################################
# # Main
# #######################################################################################

logger = None

if __name__ == "__main__":

    config = config.get_config(sys.argv)
    log.configure_logging(config['log_file_path'])
    logger = log.get_logger("galaxy_analysis")

    logger.debug("*** Starting ***")
    main(config)
    logger.debug("*** Finished ***")
