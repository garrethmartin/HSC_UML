__author__ = 'AlexH'
import sys
import numpy as np
import log
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import silhouette_samples, silhouette_score

import pandas as pd

def normalize_rows(matrix):

    for i in range(matrix.shape[0]):
        total = np.sum(matrix[i, :])
        #total = np.sqrt(np.square(matrix[i, :]).sum())
        matrix[i, :] = matrix[i, :] / total
    return matrix

def load_and_normalize(counts, min_patches, offset=1):
    indices = []
    rows = counts.shape[0]
    cols = counts.shape[1] - offset

    for i in range(rows):
        total_patches = np.sum(counts[i, offset:cols])
        if total_patches > min_patches: # and total_patches < 50:
            indices.append(i)
    indices = np.array(indices)

    large_counts = counts[indices, :]

    #gt_labels = get_gt_labels(gt_labels_file_path, large_counts)

    logger.info("normalizing data")
    samples = large_counts[:, offset:]
    samples = samples.astype(np.float64)
    #samples = normalize_rows(samples)

    a = TfidfTransformer()
    print (samples.shape)
    print (type(samples))
    samples = a.fit_transform(samples)
    print (samples.shape)
    print (type(samples))
    return large_counts, samples


def run_agg_clustering(samples, k):

    logger.info("running agg clustering")
    # agglom
    model = AgglomerativeClustering(linkage='average',
                                            connectivity=None,
                                            affinity='cosine',
                                            n_clusters=k)

    model.fit(samples.toarray())

    agglabels = model.labels_
    #aggcolors = get_colors(agglabels)
    #print "agg"
    #print agglabels

    # calculate silhouette score
    sil_score = metrics.silhouette_score(samples, agglabels, metric='cosine')
    logger.info("agg k: {0} silhouette score: {1}".format(k, sil_score))

    silhouette_values = silhouette_samples(samples, agglabels)
    #print "silhouette values: {0}".format(silhouette_values[0:10])

    return model, agglabels, silhouette_values


def run_kmeans_clustering(samples, k):
    logger.info("running kmeans")
    # kmeans takes into account object size
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(samples)
    klabels = kmeans.labels_
    #kcolors = get_colors(klabels)

    # calculate silhouette score
    sil_score = metrics.silhouette_score(samples, klabels, metric='euclidean')
    logger.info("kmeans k: {0} silhouette score: {1}".format(k, sil_score))

    silhouette_values = silhouette_samples(samples, klabels)
    #print "silhouette values: {0}".format(silhouette_values[0:10])

    #logger.info("running kmeans clustering")
    # agglom
    #model = AgglomerativeClustering(linkage='complete',
    #                                        connectivity=None,
    #                                        affinity='cosine',
    #                                        n_clusters=12)

    #model.fit(samples)
    #agglabels = model.labels_
    #aggcolors = get_colors(agglabels)
    #print "agg"
    #print agglabels
    return kmeans, klabels, silhouette_values #, kcolors

def main(config):

    counts_file_path = config['counts_file_path']
    output_folder = config['output_folder_path']
    print ("output_folder: {0} counts_file_path: {1}".format(output_folder, counts_file_path))
    logger.info("output_folder: {0} counts_file_path: {1}".format(output_folder, counts_file_path))

    algo = config['cluster_algo']
    cluster_func = None
    if algo == 'kmeans':
        cluster_func = run_kmeans_clustering
    if algo == 'agg':
        cluster_func = run_agg_clustering

    min_patches = int(config['min_pixel_count'])
    k_min = int(config['k_min'])
    k_max = int(config['k_max'])
    k_step = int(config['k_step'])

    offset = int(config['col_offset'])
    #obj_id_col = int(config['obj_id_col'])

    logger.info("min_patches:{0} k:{1} offset:{2}".format(min_patches, k_max, offset))

    logger.info("loading object counts file")

    counts_pd = pd.read_csv(counts_file_path, delimiter=",", dtype=np.int)
    counts = counts_pd.values
    #counts = np.loadtxt(counts_file_path, dtype=np.int, delimiter=',')

    large_counts, tf_idf_samples = load_and_normalize(counts, min_patches, offset=offset)

    logger.info("objects: {0}  large: {1}  min patches: {2} k min: {3} k_max {4} k_step {5}".format(
        counts.shape, large_counts.shape, min_patches, k_min, k_max, k_step))

    #sub_labels = np.zeros(large_counts.shape[0], dtype=np.int)

    for i in range(k_min, k_max, k_step):

        logger.info("tdf_idf_samples shape: {0}".format(tf_idf_samples.shape))

        model, labels, silhouette_values = cluster_func(tf_idf_samples, i)
        logger.info("labels shape: {0}".format(labels.shape))

        # output
        #kmeans_out = np.c_[large_counts, klabels]
        #aggclu_out = np.c_[large_counts, agglabels]

        logger.info("saving classification files k: {0} minpatches: {1}".format(i, min_patches))

        full_file_name = '{0}_classifications_{1}_{2}.txt'.format(algo, i, min_patches)
        labels_file_name = '{0}_classifications_labels_{1}_{2}.txt'.format(algo, i, min_patches)
        tfidf_samples_name = '{0}_tfidf_{1}_{2}.txt'.format(algo, i, min_patches)
        silhouette_values_file_name = '{0}_silhouette_values_{1}_{2}.txt'.format(algo, i, min_patches)

        #np.savetxt(output_folder + full_file_name, kmeans_out, delimiter=',', fmt='%i')
        #np.savetxt(output_folder + 'aggclu_classifications.txt', aggclu_out, delimiter=',', fmt='%i')

        kmeans_out2 = np.c_[large_counts[:, 0:offset], labels]
        #aggclu_out2 = np.c_[large_counts[:,0], agglabels]

        np.savetxt(output_folder + labels_file_name, kmeans_out2, delimiter=',', fmt='%i')
        #np.savetxt(output_folder + 'aggclu_classifications2.txt', aggclu_out2, delimiter=',', fmt='%i')

        silhouette_out = np.c_[large_counts[:, 0:offset], silhouette_values]
        np.savetxt(output_folder + silhouette_values_file_name, silhouette_out, delimiter=',', fmt='%f')

        #kres = np.c_[large_counts[:, 0], klabels]
        #aggres = np.c_[large_counts[:,0], agglabels]

        #print "kmeans: :{0}".format(kres)
        #print "agg: {0}".format(aggres)
        #print "agg: :{0} {1}".format(aggclu_out[:, 0], aggclu_out[:, -1])


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

import argparse

def get_galaxy_train_config(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--cluster_algorithm", help="the algorithm to use to group galaxies", type=str)
    parser.add_argument("-c", "--counts_file_path", help="galaxy histograms", type=str)
    parser.add_argument("-m", "--min_pixel_count", help="exclude galaxies smaller than ...", type=int)
    parser.add_argument("-k", "--k_min", help="starting K", type=int)
    parser.add_argument("-e", "--k_max", help="ending K", type=int)
    parser.add_argument("-s", "--k_step", help="K increment between K_min and K_max", type=int)
    parser.add_argument("-o", "--col_offset", help="", type=int)
    parser.add_argument("-x", "--output_folder", help="output location for classifications", type=str)
    parser.add_argument("-l", "--log_file_path", help="logs path", type=str)
    args = parser.parse_args()

    config = {}

    if hasattr(args, 'cluster_algorithm'):
        config['cluster_algo'] = args.cluster_algorithm
    if hasattr(args, 'counts_file_path'):
        config['counts_file_path'] = args.counts_file_path
    if hasattr(args, 'min_pixel_count'):
        config['min_pixel_count'] = args.min_pixel_count
    if hasattr(args, 'k_min'):
        config['k_min'] = args.k_min
    if hasattr(args, 'k_max'):
        config['k_max'] = args.k_max
    if hasattr(args, 'k_step'):
        config['k_step'] = args.k_step
    if hasattr(args, 'col_offset'):
        config['col_offset'] = args.col_offset
    if hasattr(args, 'log_file_path'):
        config['log_file_path'] = args.log_file_path
    if hasattr(args, 'output_folder'):
        config['output_folder_path'] = args.output_folder

    return config

logger = None

if __name__ == "__main__":

    config = get_galaxy_train_config(sys.argv)
    log.configure_logging(config['log_file_path'])
    logger = log.get_logger("galaxy_train")

    logger.debug("*** Starting ***")
    main(config)
    logger.debug("*** Finished ***")


"""
        max_cluster_num = np.max(klabels)
        # two level clustering
        for j in range(max_cluster_num+1):
            if klabels[klabels[:] == j].shape[0] < 300000:
                continue
            # get indices
            cluster_mask = (klabels[:] == j)
            cluster_indices = np.where(cluster_mask)[0]
            cluster_samples = large_counts[cluster_indices, offset:]
            a = TfidfTransformer()
            cluster_tf_idf_samples = a.fit_transform(cluster_samples)
            #cluster_tf_idf_samples = tf_idf_samples[cluster_mask]
            kmeans2, sub_klabels, sub_silhouette_values = run_clustering(cluster_tf_idf_samples, 50)
            sub_labels[cluster_indices] = sub_klabels
            #
        # get cluster group


"""
