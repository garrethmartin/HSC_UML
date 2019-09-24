__author__ = 'AlexH'
import sys
from sklearn.neighbors.nearest_centroid import NearestCentroid
import numpy as np
import config
import log

def main(config):

    model_classifications = config['model_classifications']
    unseen_objects = config['unseen_objects_file']
    output_file_path = config['output_file_path']
    logger.info("model: {0}".format(model_classifications))
    logger.info("new data: {0}".format(unseen_objects))
    logger.info("output path: {0}".format(output_file_path))

    data = np.loadtxt(model_classifications, delimiter=',', dtype=np.int)
    labels = data[:, -1] # labels are the last column
    samples = data[:, 1:-1] # first column is object id so take middle columns

    logger.info("identifying centroids")
    clf = NearestCentroid(metric='cosine')
    clf.fit(samples, labels)
    logger.info("num centroids: {0}".format(len(clf.centroids_)))

    logger.info("load unseen objects")
    unseen_samples = np.loadtxt(unseen_objects, delimiter=',', dtype=np.int)
    logger.info("num new galaxies: {0}".format(len(unseen_samples)))

    logger.info("classify unseen objects")
    predictions = clf.predict(unseen_samples[:, 1:])

    logger.info("save labels")
    output_labels = np.c_[unseen_samples[:, 0], predictions]
    np.savetxt(output_file_path, output_labels, fmt='%i')

# #######################################################################################
# # Main
# #######################################################################################

logger = None

if __name__ == "__main__":

    config = config.get_config(sys.argv)
    log.configure_logging(config['log_file_path'])
    logger = log.get_logger("galaxy_classify")

    logger.debug("*** Starting ***")
    main(config)
    logger.debug("*** Finished ***")