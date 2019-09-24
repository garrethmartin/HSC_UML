__author__ = 'ah14aeb'
import numpy

def normalize_general_features(samples, mean, std):

    temp_data = numpy.array(samples)

    min_ = numpy.min(temp_data, axis=0)
    max_ = numpy.max(temp_data, axis=0)
    mean1_ = numpy.mean(temp_data, axis=0)
    std1_ = numpy.std(temp_data, axis=0)

    print("model mean: {0}".format(mean))
    print(" mean differences: {0}".format((mean1_ - mean) / mean1_ * 100))
    print("model std: {0}".format(std))
    print(" std differences: {0}".format((std1_ - std) / std1_ * 100))

    # normalize
    temp_data -= mean
    temp_data /= std

    min2_ = numpy.min(temp_data, axis=0)
    max2_ = numpy.max(temp_data, axis=0)
    mean2_ = numpy.mean(temp_data, axis=0)
    std2_ = numpy.std(temp_data, axis=0)

    ncols = temp_data.shape[1]

    for i in range(ncols):
        print("feature no: {0} before norm::  min: {1:.4f}\tmax: {2:.4f}\tmodel mean: {9:.4f}\tmean: {3:.4f}\tmodel std: {10:.4f}\tstd: {4:.4f}   after norm:: min: {5:.4f}\tmax: {6:.4f}\tmean: {7:.4f}\tstd: {8:.4f}".format(i+1,
                    min_[i], max_[i], mean1_[i], std1_[i], min2_[i], max2_[i], mean2_[i], std2_[i], mean[i], std[i]))

    for i in range(ncols):
        print("{0}\t{1:.4f}\t{2:.4f}\t{3:.4f}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\t{8:.4f}".format(i+1,
                    min_[i], max_[i], mean1_[i], std1_[i], min2_[i], max2_[i], mean2_[i], std2_[i]))

    return temp_data, mean1_, std1_


def normalize_model_features(samples):

    temp_data = numpy.array(samples)

    min_ = numpy.min(temp_data, axis=0)
    max_ = numpy.max(temp_data, axis=0)
    mean1_ = numpy.mean(temp_data, axis=0)
    std1_ = numpy.std(temp_data, axis=0)

    # normalize
    temp_data -= mean1_
    temp_data /= std1_

    min2_ = numpy.min(temp_data, axis=0)
    max2_ = numpy.max(temp_data, axis=0)
    mean2_ = numpy.mean(temp_data, axis=0)
    std2_ = numpy.std(temp_data, axis=0)

    ncols = temp_data.shape[1]

    for i in range(ncols):
        print("feature no: {0} before norm::  min: {1:.4f}\tmax: {2:.4f}\tmean: {3:.4f}\tstd: {4:.4f}   after norm:: min: {5:.4f}\tmax: {6:.4f}\tmean: {7:.4f}\tstd: {8:.4f}".format(i+1,
                    min_[i], max_[i], mean1_[i], std1_[i], min2_[i], max2_[i], mean2_[i], std2_[i]))

    for i in range(ncols):
        print("{0}\t{1:.4f}\t{2:.4f}\t{3:.4f}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\t{8:.4f}".format(i+1,
                    min_[i], max_[i], mean1_[i], std1_[i], min2_[i], max2_[i], mean2_[i], std2_[i]))

    return temp_data, mean1_, std1_


def native_pca(X):
    n_samples, n_features = X.shape

    Y = X / numpy.sqrt(X.shape[0]-1)

    U, S, V = numpy.linalg.svd(Y, full_matrices=False)

    # print variances
    get_native_variance(S, n_samples)

    return (U, S, V)

def get_native_variance(S, n_samples):
    explained_variance_ = (S ** 2) / n_samples
    explained_variance_ratio_ = (explained_variance_ /
                                  explained_variance_.sum())
    #print explained_variance_ratio_[0:10]
    #print explained_variance_ratio_[0:2].sum()

    pc_ratios = []
    for ratio in explained_variance_ratio_:
        pc_ratios.append(int(ratio * 10000) / 100.0)

    print ("variances: {0}".format(pc_ratios))
    return pc_ratios

def native_transform(X, components, ncomps=-1):
    X = numpy.array(X, copy=True)
    if ncomps == -1:
        X_transformed = numpy.dot(X, components.T)
    else:
        X_transformed = numpy.dot(X, components[0:ncomps].T)

    return X_transformed
