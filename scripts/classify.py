#!/usr/bin/env python
from __future__ import print_function
import argparse
import glob
from graph_clustering import run_classify

parser = argparse.ArgumentParser()
parser.add_argument('-bd', '--base_dir', type=str, default=None, help='Base directory')
parser.add_argument('-dd', '--data_dir', type=str, default=None, help='Data directory')
parser.add_argument('-im', '--img_names', type=list, default=None, help='Image filenames')
parser.add_argument('-il', '--img_list', type=list, default=None, help='File containing list of image filenames')
parser.add_argument('-ib', '--bounds', type=str, default=None, help='Image bounds')
parser.add_argument('-wl', '--bands', type=list, default=None, help='Image bands')
parser.add_argument('-oi', '--out_id', type=float, default=1, help='Output id for the model')
parser.add_argument('-pd', '--patch_dir', type=str, default='ps', help='Patch sub-directory')
parser.add_argument('-ps', '--patch_size', type=float, default=10, help='Patch radius in pixels')
parser.add_argument('-nn', '--n_nodes', type=float, default=15000, help='Number of nodes in the GNG graph')
parser.add_argument('-ct', '--HC_target', type=float, default=800, help='Target clusters of HC clustering')
parser.add_argument('-nt', '--n_threads', type=float, default=1, help='Number of CPU threads')
parser.add_argument('-ns', '--n_samples', type=float, default=1000000, help='Number of samples to process before adding a new node')
parser.add_argument('-ni', '--n_iterations', type=float, default=50000, help='Total number of GNG iterations')
parser.add_argument('-mt', '--metric', type=str, default='pspearson', help='Metric used to measure distance [pspearson, cosine, linear]')

parser.add_argument('-pe', '--extract', action='store_true', help='Perform extraction step')
parser.add_argument('-pl', '--parallel', action='store_true', help='Use with --extract to perform extraction step in parallel')
parser.add_argument('-ng', '--gng', action='store_true', help='Perform growing neural gas step')
parser.add_argument('-hc', '--h_cluster', action='store_true', help='Perform heirarchical clustering step')
parser.add_argument('-cc', '--conn_comps', action='store_true', help='Perform connected component step')
parser.add_argument('-gt', '--galaxy_train', action='store_true', help='Perform k-means clustering on galaxy feature vectors and produce catalogues')
args = parser.parse_args()

files = glob.glob(args.img_names)

run_classify(dir_base=args.base_dir, dir_data=args.data_dir, files=args.img_names, file_list=args.img_list,
             bounds=args.bounds, bounds_list=args.bounds, bands=args.bands,
             output_id=args.out_id, patch_folder=args.patch_dir, patch_size=args.patch_size,
             nodes=args.n_nodes, clustering_target=args.HC_target, threads=args.n_threads,\
             metric=args.metric, n_samples=args.n_samples, iterations=args.n_iterations,
             patch_extraction=args.extract,
             parallel_extract=args.parallel,
             GNG_model=args.gng,
             hierarchical_clustering=args.h_cluster,
             connected_components=args.conn_comps,
             group_train=args.galaxy_train)
