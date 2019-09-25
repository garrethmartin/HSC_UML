# ***README*** for `classify.py` / `graph_clustering`

### Update history

*September 2019*: - HSC DR1 UDEEP catalogue added

*Near future*: - Add DR2 DEEP/UDEEP catalogues with varying *k*
      	       - Add code to run the algorithm w/ examples and documentation

***

### Reference: [***Martin 2019b***](https://arxiv.org/abs/1909.10537 "arXiv")

### Contact: [garrethmartin@arizona.edu](mailto:garrethmartin@arizona.edu "email")

***

### Purpose:
Clusters objects found in a list of astronomical images by their visual similarity. Objects are sorted into *k* groups and a catalogue containing object centroids, group number, size in pixels and silhouette score is output.

### Prerequisites:
* numpy
* scipy
* astropy
* configobj
* sklearn
* joblib
* matplotlib

* [dotnetcore SDK](https://dotnet.microsoft.com/download "dotnetcore")

### Installation on Python 2.7 (3 not tested):

`pip install galaxy_graph`

or build from source

`python setup.py install galaxy_graph`

### Usage:

#### Using the built-in script:

      usage: classify.py [-h] [-bd BASE_DIR] [-dd DATA_DIR] [-im IMG_NAMES]
                         [-il IMG_LIST] [-ib BOUNDS] [-wl BANDS] [-oi OUT_ID]
                         [-pd PATCH_DIR] [-ps PATCH_SIZE] [-nn N_NODES]
                         [-ct HC_TARGET] [-nt N_THREADS] [-ns N_SAMPLES]
                         [-ni N_ITERATIONS] [-mt METRIC] [-pe] [-pl] [-ng] [-hc]
                         [-cc] [-gt]

      optional arguments:
        -h, --help            show this help message and exit
        -bd BASE_DIR, --base_dir BASE_DIR
                              Base directory
        -dd DATA_DIR, --data_dir DATA_DIR
                              Data directory
        -im IMG_NAMES, --img_names IMG_NAMES
                              Image filenames
        -il IMG_LIST, --img_list IMG_LIST
                              File containing list of image filenames
        -ib BOUNDS, --bounds BOUNDS
                              Image bounds
        -wl BANDS, --bands BANDS
                              Image bands
        -oi OUT_ID, --out_id OUT_ID
                              Output id for the model
        -pd PATCH_DIR, --patch_dir PATCH_DIR
                              Patch sub-directory
        -ps PATCH_SIZE, --patch_size PATCH_SIZE
                              Patch radius in pixels
        -nn N_NODES, --n_nodes N_NODES
                              Number of nodes in the GNG graph
        -ct HC_TARGET, --HC_target HC_TARGET
                              Target clusters of HC clustering
        -nt N_THREADS, --n_threads N_THREADS
                              Number of CPU threads
        -ns N_SAMPLES, --n_samples N_SAMPLES
                              Number of samples to process before adding a new node
        -ni N_ITERATIONS, --n_iterations N_ITERATIONS
                              Total number of GNG iterations
        -mt METRIC, --metric METRIC
                              Metric used to measure distance [pspearson, cosine,
                              linear]
        -pe, --extract        Perform extraction step
        -pl, --parallel       Use with --extract to perform extraction step in
                              parallel
        -ng, --gng            Perform growing neural gas step
        -hc, --h_cluster      Perform heirarchical clustering step
        -cc, --conn_comps     Perform connected component step
        -gt, --galaxy_train   Perform k-means clustering on galaxy feature vectors
                              and produce catalogues


#### Importing the package

      from graph_clustering import run_classify
      >>> run_classify(dir_base=dir_base, dir_data=dir_data, files=files, bounds=bounds,
                       bands=bands, output_id=output_id, patch_folder=patch_folder,
                       patch_size=patch_size, nodes=nodes, clustering_target=clusters,
                       threads=threads, metric=metric, n_samples=n_samples,
                       iterations=iterations,patch_extraction=True, parallel_extract=True,
                       GNG_model=True, hierarchical_clustering=True,
                       connected_components=True, group_train=True)
                    
     >>> run_classify(dir_base=dir_base, dir_data=dir_data, **file_list=file_list**, **bounds_list=bounds_list**,
                      bands=bands, output_id=output_id, patch_folder=patch_folder,
                      patch_size=patch_size, nodes=nodes, clustering_target=clusters,
                      threads=threads, metric=metric, n_samples=n_samples,
                      iterations=iterations,patch_extraction=True, parallel_extract=True,
                      GNG_model=True, hierarchical_clustering=True,
                      connected_components=True, group_train=True)
