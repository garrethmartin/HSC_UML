__author__ = 'AlexH'
import sys
import numpy as np
import config
import log
from astropy.io import fits as pyfits
#from astro.mlhelper import pcahelper, feature_helper
from helpers import feature_helper
from helpers import normalisation as pcahelper
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import axes3d, Axes3D
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn import manifold
from sklearn.feature_extraction.text import TfidfTransformer

def plot_scatter_2d(orig, pca_data, principle_comps, labels, title="PCA", save_file=False, file_path=""):

    def onscatterpick(event):
        #thisline = event.artist
        index = event.ind
        print ('onpick points:{0} {1}'.format(index, orig[index, 0]))

    gs1 = gridspec.GridSpec(1, 1)
    fig = plt.figure()
    #ax1 = fig.add_subplot(gs1[0])
    #ax1 = fig.add_subplot(gs1[0], projection='3d')
    ax1 = Axes3D(fig)

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
        #total = np.sqrt(np.square(matrix[i, :]).sum())
        matrix[i, :] = matrix[i, :] / total
    return matrix

def main(config):

    counts_file_path = config['counts_file_path']
    output_folder = config['output_folder_path']
    min_object_size_in_patches = int(config['min_patch_count'])
    k = int(config['k'])

    logger.info("loading object counts file")
    #gt_labels_file_path = base_path + 'abell2744_conn_comps/labels.txt'
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

    #gt_labels = get_gt_labels(gt_labels_file_path, large_counts)

    logger.info("normalizing data")
    samples = large_counts[:, 1:]
    samples = samples.astype(np.float64)
    #samples = normalize_rows(samples)

    a = TfidfTransformer()
    print (samples.shape)
    type(samples)
    samples = a.fit_transform(samples)
    print (samples.shape)
    samples = samples.toarray()
    type(samples)
    #samples = feature_helper.normalize_features(samples)

    logger.info("running pca")
    #U, S, V = pcahelper.native_pca(samples)
    #components_ = V
    #vars = pcahelper.get_native_variance(S, samples.shape[0])
    #pca_samples = pcahelper.native_transform(samples, components_, -1)

    #n_components = 4
    #mds = manifold.MDS(n_components, max_iter=100, n_init=1)
    #pca_samples = mds.fit_transform(samples)

    principle_comps = np.array([1,2,3])

    logger.info("objects: {0}  large: {1}  min patches: {2}".format(rows, large_counts.shape[0], min_patches))

    logger.info("running DBSCAN")
    from sklearn.cluster import DBSCAN
    from sklearn import metrics
    db = DBSCAN(eps=0.15, min_samples=10, algorithm='brute', metric='cosine').fit(samples)
    dblabels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(dblabels)) - (1 if -1 in dblabels else 0)
    if n_clusters_ > 2:
        print ("error clusters: {0}".format(n_clusters_))
    unique_labels = set(dblabels)
    #colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    colors = []
    for i in range(samples.shape[0]):
        if dblabels[i] == 0:
            colors.append('r')
        else:
            colors.append('y')

    logger.info("running kmeans")
    # kmeans takes into account object size
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(samples)
    klabels = kmeans.labels_
    #kcolors = get_colors(klabels)

    logger.info("running agg clustering")
    # agglom
    model = AgglomerativeClustering(linkage='complete',
                                            connectivity=None,
                                            affinity='cosine',
                                            n_clusters=k)

    model.fit(samples)
    agglabels = model.labels_
    #aggcolors = get_colors(agglabels)
    print ("agg")
    print (agglabels)

    # output
    dbscan_out = np.c_[large_counts, dblabels]
    kmeans_out = np.c_[large_counts, klabels]
    aggclu_out = np.c_[large_counts, agglabels]

    logger.info("saving classification files")
    np.savetxt(output_folder + 'dbscan_classifications.txt', dbscan_out, delimiter=',', fmt='%i')
    np.savetxt(output_folder + 'kmeans_classifications.txt', kmeans_out, delimiter=',', fmt='%i')
    np.savetxt(output_folder + 'aggclu_classifications.txt', aggclu_out, delimiter=',', fmt='%i')

    dbscan_out2 = np.c_[large_counts[:,0], dblabels]
    kmeans_out2 = np.c_[large_counts[:,0], klabels]
    aggclu_out2 = np.c_[large_counts[:,0], agglabels]

    np.savetxt(output_folder + 'dbscan_classifications2.txt', dbscan_out2, delimiter=',', fmt='%i')
    np.savetxt(output_folder + 'kmeans_classifications2.txt', kmeans_out2, delimiter=',', fmt='%i')
    np.savetxt(output_folder + 'aggclu_classifications2.txt', aggclu_out2, delimiter=',', fmt='%i')


    #kres = np.c_[large_counts[:,0], klabels]
    #aggres = np.c_[large_counts[:,0], agglabels]

    #print "kmeans: :{0}".format(kres)
    #print "agg: {0}".format(aggres)
    #print "agg: :{0} {1}".format(aggclu_out[:, 0], aggclu_out[:, -1])
    #print "dbscan: {0} {1}".format(dbscan_out[:, 0], dbscan_out[:, -1])

    #plot_scatter_2d(large_counts, pca_samples, principle_comps, kcolors) #gt_labels aggcolors


def get_colors(labels):
    cols = ['r','b','y','g','b','c', 'r','b','y','g','b','c', 'r','b','y','g','b','c','r','b','y','g','b','c','r','b','y','g','b','c','r','b','y','g','b','c','r','b','y','g','b','c','r','b','y','g','b','c','r','b','y','g','b','c']
    out_cols = []
    for i in range(len(labels)):
        out_cols.append(cols[labels[i]])
    return out_cols

def get_gt_labels(gt_labels_file_path, samples):
    gt_labels = np.loadtxt(gt_labels_file_path, dtype=np.int, delimiter=' ')
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
    logger = log.get_logger("galaxy_train")

    logger.debug("*** Starting ***")
    main(config)
    logger.debug("*** Finished ***")
