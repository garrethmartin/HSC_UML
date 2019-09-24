from __future__ import print_function
from scipy.ndimage import binary_erosion, binary_dilation, label, generate_binary_structure
from shutil import copy
import glob
import numpy as np
from astropy.io import fits 
from astropy.visualization import make_lupton_rgb
import re
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import os

path = os.path.abspath(__file__)
code_path = os.path.dirname(path)

def run_classify(dir_base=None, dir_data=None, files=None, file_list=None,
                 bounds=None, bounds_list=None,
                 bands=None,
                 threads=1,
                 output_id=1, patch_folder='ps', name_run='default',
                 patch_size=10, nodes=1000000, n_samples=600000, iterations=70000,
                 clustering_target=800, metric='pspearson',
                 pix_min=8, 
                 patch_extraction=False,
                 parallel_extract=False,
                 GNG_model=False, 
                 hierarchical_clustering=False,
                 connected_components=False,
                 group_train=False,
                 make_montage=False,
                 ignore=[None]):
    """
    Clusters objects found in a list of astronomical images by their visual similarity.
    """
    if dir_base is None:
        raise ValueError('dir_base must be specified and of type string')
    if dir_data is None:
        raise ValueError('dir_data must be specified and of type string')
    if files is None and file_list is None:
        raise SyntaxError('Either files or file_list must be specified')
    if bounds is None and bounds_list is None:
        raise SyntaxError('Either bounds or bounds_list must be specified')
    if bands is None:
        raise SyntaxError('Specify band names')

    if dir_base == '.':
	dir_base = os.getcwd()
    
    if file_list is not None:
        if files is not None:
            print('file and file_list both specified... using file_list')
            f = np.loadtxt(file_list, dtype=str)
            f = f.tolist()
            n = len(bands)
            files = [f[i * n:(i + 1) * n] for i in range((len(f) + n - 1) // n )]
            
    if bounds_list is not None:
        if bounds is not None:
            print('bounds and bounds_list both specified... using bounds_list')
            f = np.loadtxt(bounds_list, dtype=int)
            f = f.tolist()
            bounds = [f[i * 4:(i + 1) * 4] for i in range((len(f) + 4 - 1) // 4 )]

    # Make directory if needed
    print('-----------------')
    print('INITIAL SETUP ...')
    print('SETTING UP DIRECTORY ...')
    if glob.glob(dir_base+'/'+dir_data) == []:
        os.mkdir(dir_base+'/'+dir_data)
    # Copy prerequisite files
    os.chdir(dir_base+'/'+dir_data)
    copy_prereqs(dir_base, dir_data)
    os.chdir(dir_base)
    # Write init file    
    os.chdir(dir_base+'/'+dir_data)
    #write_init(dir_base, dir_data)
    write_init(code_path, dir_base, dir_data)
    os.chdir(dir_base)
    # Write config files
    os.chdir(dir_base+'/'+dir_data)
    if glob.glob('config') == []:
        os.mkdir('config')
    write_config(output_id, ','.join(bands), len(bands), pix_min=pix_min, threads=threads, metric=metric,
                 GNG_nodes=nodes, GNG_iterations=iterations)
    os.chdir(dir_base)
    # Write image location and sky area files
    os.chdir(dir_base+'/'+dir_data)
    write_img(output_id, files, bands, ignore=ignore)
    write_sky(output_id, name_run, bounds, ignore=ignore)
    os.chdir(dir_base)
    # Run patch extraction
    print('-----------------')
    if patch_extraction:
        print('PATCH EXTRACTION ...')
        if parallel_extract:
            os.chdir(dir_base+'/'+dir_data)
            os.system('bash run_extract_parallel.sh '+str(output_id)+' '+patch_folder+' '+str(patch_size)+' '+str(threads))
            os.chdir(dir_base)
        else:
            os.chdir(dir_base+'/'+dir_data)
            os.system('bash run_extract.sh '+str(output_id)+' '+patch_folder+' '+str(patch_size))
            os.chdir(dir_base)
        print('-----------------')
    
    if glob.glob(dir_base+'/'+dir_data+'/'+patch_folder+'/output_'+str(output_id)+'/'+str(1)) == []:
        raise Exception('Run patch extraction first!')
    
    # Model location
    os.chdir(dir_base+'/'+dir_data)
    write_model(1, patch_folder+'/output_'+str(output_id))
    os.chdir(dir_base)
    # Run GNG algorithm
    
    if GNG_model:
        print('GNG MODELING ...')
        os.chdir(dir_base+'/'+dir_data)
        os.system('bash run_gng.sh '+patch_folder+' '+str(n_samples)+' '+str(output_id))
        os.chdir(dir_base)
        print('-----------------')
    # Run heirarchical clustering algorithm
    if hierarchical_clustering:
        print('HEIRARCHICAL CLUSTERING ...')
        os.chdir(dir_base+'/'+dir_data)
        os.system('bash run_agg.sh '+str(output_id))
        os.chdir(dir_base)
        print('-----------------')
    # Check the clustering values
            
    if glob.glob(dir_base+'/'+dir_data+'/model'+str(output_id)+\
                                        '/'+metric+'/*mapping*') == []:
        raise Exception('Run GNG / HC first!')
    
    clustering_files = sorted(glob.glob(dir_base+'/'+dir_data+'/model'+str(output_id)+\
                                        '/'+metric+'/*mapping*'))
    values = np.array([ re.split('[_,.]', file)[-4:-1] for file in clustering_files ])
    GNG1 = np.array([ value[0]+'.'+value[1] for value in values ])
    GNG2 = values[:,2]
    pick = np.where(np.abs(np.int32(GNG2) - clustering_target) == \
                    np.min(np.abs(np.int32(GNG2) - clustering_target)))[0][0]
    # Run connected component algorithm with appropriate values
    if connected_components:
        print('CONNECTED COMPONENTS ...')
        os.chdir(dir_base+'/'+dir_data)
        os.system('bash run_conncomps.sh '+patch_folder+' '+str(output_id)+' '+'model'\
                  +str(output_id)+' '+str(GNG2[pick])+' '+str(GNG1[pick]))
        os.chdir(dir_base)
        print('-----------------')
    # Split into groups
    if group_train:
        print('TRAINING ON OBJECTS...')
        os.chdir(dir_base+'/'+dir_data+'/model'+str(output_id)+'/conncomps/')
        if glob.glob(dir_base+'/'+dir_data+'/model'+str(output_id)+'/galtrain/') == []:
            os.mkdir(dir_base+'/'+dir_data+'/model'+str(output_id)+'/galtrain/')
        object_counts_files = glob.glob('object_counts*')
        if len(object_counts_files) > 1:
            outf = 'concatenated_counts_'+str(output_id)+'.txt'
            if glob.glob(outf) == []:
                with open(outf, 'w') as outfile:
                    for count_file in object_counts_files:
                          with open(count_file) as infile:
                                for line in infile:
                                    outfile.write(line)
        else:
            outf = object_counts_files[0]
        print(outf)
        os.chdir(dir_base)
        os.chdir(dir_base+'/'+dir_data)
        os.system('bash run_galaxy_train.sh kmeans model'+str(output_id)+' '+outf)
        os.system('mv '+dir_base+'/'+dir_data+'/model'+str(output_id)+'/conncomps/kmeans* '+\
                  dir_base+'/'+dir_data+'/model'+str(output_id)+'/galtrain')
        os.chdir(dir_base)
        print('-----------------')
    # Make montage of groups
    if make_montage:
        print('PRODUCING MONTAGE')
        os.chdir(dir_base+'/'+dir_data)
        os.system('bash run_montage.sh')
        os.chdir(dir_base)
        print('-----------------')

def write_config(output_id, lambdas, n_bands, pix_min=8, threads=4, GNG_iterations=250, GNG_nodes=15000, metric='pspearson', min_sigma=1):
    f = open('config/auto_feature_extraction_config.ini', 'w')
    f.write('required_wavelengths='+lambdas+'\n')
    f.write('sigma_multipliers='+str(min_sigma)+','+str(min_sigma+2)+\
            ','+str(min_sigma+4)+','+str(min_sigma+6)+'\n')
    f.write('min_sigma_multiplier='+str(min_sigma)+'\n')
    f.close()
    
    f = open('config/auto_agglom_config', 'w')
    f.write('outputFolder=/agglom/\n')
    f.write('nodePositions=node_position_list.txt\n')
    f.write('nodeClusterIndex=node_cluster_index_.txt\n')
    f.write('clusterCentres=cluster_centeres.txt\n')
    f.write('threshold=1\n')
    f.write('useNodesNotCentroids=true\n')
    f.write('metric='+metric+'\n') # cosine / !pspearson! / euclidean
    f.write('num_threads='+str(threads)+'\n') # Number of physical cores
    f.write('num_images='+str(n_bands)) # Needed for non-cosine metric
    f.close()

    f = open('config/auto_conncomps.txt', 'w') # # Number of physical cores
    f.write('agglom_folder_name=/'+metric+'/\n') # cosine / !pspearson! / euclidean
    f.write('num_threads='+str(threads)+'\n')
    f.write('node_positions_file_name=node_position_list.txt\n')
    f.write('samples_file_name=samples.csv\n')
    f.write('positions_file_name=positions.csv\n')
    f.write('sigma_file_paths=/gen_sigma7_positions_mask_'+str(output_id)+'.txt,/gen_sigma3_positions_mask_'+str(output_id)+'.txt\n')
    f.write('patch_size=2\n') # Patch overlap to be considered part of the same object
    f.write('save_slices=False\n')
    f.write('min_object_size_in_patches='+str(pix_min)+'\n')
    f.write('dataspace_name=/entry/samples\n')
    f.write('num_images='+str(n_bands)+'\n')
    f.write('metric='+metric+'\n') # cosine / !pspearson! / euclidean
    f.write('hac_folder='+metric+'\n') # cosine / !pspearson! / euclidean
    f.write('log_all_samples=true\n')
    f.write('use_centroids=true\n')
    f.close()
    
    f = open('config/atlas_gng_config', 'w')
    f.write('samples_file_name=samples.hd5'+'\n')
    f.write('mean_normalize=false'+'\n')
    f.write('zscore_normalize=true'+'\n')
    f.write('metric=1'+'\n')
    f.write('output_log=true'+'\n')
    f.write('write_intermediate=false'+'\n')
    f.write('quantisation_error=false'+'\n')
    f.write('log_samples=true'+'\n')
    f.write('multiple_sky_areas=true'+'\n')
    f.write('dataspaceName=/entry/samples'+'\n')
    f.write('max_nodes='+str(GNG_nodes)+'\n')
    f.write('num_threads='+str(threads)+'\n')
    f.write('num_iterations='+str(GNG_iterations)+'\n')
    f.close()

    
def write_init(code_path, dir_base, dir_data):
    f = open('init.sh', 'w')
    f.write('CODE_FOLDER_NIX='+code_path+'\n')
    f.write('CODE_FOLDER=$CODE_FOLDER_NIX\n')
    f.write('BASE_FOLDER_NIX='+dir_base+'\n')
    f.write('BASE_FOLDER=$BASE_FOLDER_NIX\n')
    f.write('\n')
    f.write('if grep -q Microsoft /proc/version; then\n')
    f.write('  DOTNETBIN=dotnet.exe\n')
    f.write('  ROOT_FOLDER=$BASE_FOLDER\\\\'+dir_data+'\\\\\n')
    f.write('  ROOT_FOLDER_NIX=$BASE_FOLDER_NIX/'+dir_data+'/\n')
    f.write('  CODE_FOLDER=$BASE_FOLDER/code/\n')
    f.write('  PYTHON_CODE_PATH=$CODE_FOLDER_NIX/code\n')
    f.write('else\n')
    f.write('  DOTNETBIN=dotnet\n')
    f.write('  ROOT_FOLDER=$BASE_FOLDER/'+dir_data+'/\n')
    f.write('  CODE_FOLDER=$CODE_FOLDER_NIX/code/\n')
    f.write('  ROOT_FOLDER_NIX=$ROOT_FOLDER\n')
    f.write('  PYTHON_CODE_PATH=$CODE_FOLDER\n')
    f.write('fi\n\n')
    f.write('export PYTHONPATH=$PYTHON_CODE_PATH/python/algos/astro/')
    f.close


def write_img(image_id, files, bands, ignore=[None]):
    f = open('image_files_'+str(image_id)+'.txt', 'w')
    f.write('id,sky_area_id,wavelength,file_name\n')
    id_img = 1
    id_sky = 1
    for files_0 in files:
        if ~np.in1d(id_sky, ignore):
            for file, band in zip(files_0, bands):
                f.write(str(id_img)+','+str(id_sky)+','+band+','+file+'\n')
                id_img += 1
        id_sky += 1
    f.close()


def write_sky(image_id, field, bounds, ignore=[None]):
    f = open('sky_areas_'+str(image_id)+'.txt', 'w')
    f.write('id,field,field_rect,sigma_rect\n')
    id_img = 1
    for bound in bounds:
        if ~np.in1d(id_img, ignore):
            f.write(str(id_img)+','+field+','+str(bound[0])+'-'+str(bound[1])+'-'+str(bound[2])+'-'+
                    str(bound[3])+','+'None'+'\n')
        id_img += 1
    f.close()

    
def write_model(image_id, output_folder):
    f = open('model_folders.txt', 'w')
    f.write(str(image_id)+','+str(output_folder))
    f.close()

    
def copy_prereqs(dir_base, dir_data):
    dir_p = code_path+'/prereqs'
    print(dir_base+'/'+dir_data+'/')
    print(dir_p+'/')
    files = ['run_extract.sh',
             'run_extract_parallel.sh',
             'run_gng.sh',
             'run_agg.sh',
             'run_conncomps.sh',
             'run_galaxy_train.sh',
             'run_montage.sh']
    for file in files:
        if glob.glob(dir_base+'/'+dir_data+'/'+file) == []:
            copy(dir_p+'/'+file, dir_base+'/'+dir_data+'/'+file)
            print('copying '+ file)
            
            
def fits_lupton(dir_base,files, cent=None, bounds=None, img_pix=64, norm_data=None):
    image_b, image_g, image_r = [fits.getdata(dir_base+'/images/'+file) for file in files]
    if norm_data != None:
        min_0  = (np.min(image_r[image_r > 0]) + np.min(image_r[image_g > 0]) + np.min(image_r[image_b > 0])) / 3.
        image_b, image_g, image_r = [ (image_i + min_0)/norm_data for image_i in [image_b, image_g, image_r] ]
    if bounds == None:
        image = make_lupton_rgb(image_r[cent[0]-img_pix:cent[0]+img_pix,cent[1]-img_pix:cent[1]+img_pix],
                                image_g[cent[0]-img_pix:cent[0]+img_pix,cent[1]-img_pix:cent[1]+img_pix],
                                image_b[cent[0]-img_pix:cent[0]+img_pix,cent[1]-img_pix:cent[1]+img_pix],
                                stretch=0.5, Q=15)
        extent = [cent[0]-img_pix,cent[0]+img_pix,cent[1]-img_pix,cent[1]+img_pix]
    
    if cent == None:
        image = make_lupton_rgb(image_r[bounds[0]:bounds[1],bounds[2]:bounds[3]],
                                image_g[bounds[0]:bounds[1],bounds[2]:bounds[3]],
                                image_b[bounds[0]:bounds[1],bounds[2]:bounds[3]],
                                stretch=0.5, Q=15)
        extent = [bounds[0],bounds[1],bounds[2],bounds[3]]
    return image, extent
            
    
def auto_detect_good(image_data, min_counts=20000., data_min = 0.0, data_max=0.05):
    image_shape = image_data.shape
    image_mask = np.zeros_like(image_data)
    image_mask[np.where((image_data > data_min) & (image_data < data_max))[0:2]] = 1
    out = binary_erosion(image_mask, border_value=1, origin=0)
    out = binary_dilation(out, origin=0)
    labels, nlabels = label(out)
    r, counts = np.unique(labels, return_counts=True)
    label_inds = r[counts > min_counts]
    if len(label_inds) > 1:
        means = [np.mean(image_data[labels == i]) for i in label_inds]
        cut_regions = r[label_inds][means != np.max(means)]
        good = np.ones_like(image_data, dtype=np.bool)
        for cut_region in cut_regions:
            good[labels == cut_region] = 0
        return good
    else:
        return np.ones_like(image_data, dtype=np.bool)
    

def get_file_names(base_dir, dir_data, output_id):
    f = np.genfromtxt(base_dir+dir_data+'image_files_'+str(output_id)+'.txt', dtype=str,
                      skip_header=True, delimiter=',')
    sky_id = np.int32(f[:,1])
    img_id = np.int32(f[:,0])
    image_file = f[:,3]

    files = []
    sub = []
    s_id_0 = np.min(sky_id)
    for s_id, i_id, img in zip(sky_id, img_id, image_file):
        if s_id > s_id_0:
            s_id_0 = s_id
            files.append(sub)
            sub = []
            sub.append(img)
        else:
            sub.append(img)
    files.append(sub)
    
    return files


def get_object_catalogue(base_dir, dir_data, output_id):
    dir_hists = glob.glob(base_dir+dir_data+'/model'+str(output_id)+'/conncomps/object_counts_*')
    for i, hists in enumerate(dir_hists):
        hist_data_i = np.loadtxt(hists, delimiter=',')
        hist_shape = hist_data_i.shape
        end = re.findall('_[0-99999]*_[0-99999]*.txt', hists)[0]
        end = re.split('[_,.]', end)
        image_st = int(end[2])-1
        if i == 0:
            hist_data = hist_data_i
            image_id = np.array([image_st]*hist_shape[0])
        else:
            hist_data = np.vstack([hist_data, hist_data_i])
            image_id = np.concatenate((image_id, np.array([image_st]*hist_shape[0])))

    dir_poss = glob.glob(base_dir+dir_data+'/model'+str(output_id)+'/conncomps/object_catalogue_*')
    for i, poss in enumerate(dir_poss):
        pos_data_i = np.loadtxt(poss, delimiter=',', dtype=np.int32)
        if i == 0:
            pos_data = (pos_data_i)
        else:
            pos_data = np.vstack([pos_data, pos_data_i])
    return pos_data, hist_data, image_id


def similarity_search(hist_data, target_id, metric='euclidean'):
    a = TfidfTransformer()
    samples_t = a.fit_transform(hist_data[:,1:])
    samples_t = samples_t.toarray()
    samples_t = samples_t / np.expand_dims(np.sum(samples_t, axis=1), 1)
                      
    sample_0 = np.expand_dims(samples_t[target_id][1:], 0)
    samples_all = samples_t[:,1:]
    dist = cdist(sample_0, samples_all, metric=metric).flatten()
    return samples_t, dist


def plot_bound(base_dir, files, object_ids, y_cents, x_cents, img_pix = 64, bounds=None, plot_in_bounds=False, norm_data=None, shape=None, number=False):
    n_obj = len(object_ids)
    n_square = np.int32(np.ceil(np.sqrt(n_obj)))
    if bounds != None: N_bound, S_bound, W_bound, E_bound = bounds
    if shape == None:
        fig, axs = plt.subplots(ncols=n_square, nrows=n_square, figsize=(8,8))
    else:
        fig, axs = plt.subplots(ncols=shape[0], nrows=shape[1], figsize=(shape[0],shape[1]))
    if n_square > 1:
        ax_list = axs.ravel()
    else:
        ax_list = [axs]
        
    if number:
        n_inc = 1
        
    for i, (ax, object_id, x_cent, y_cent) in enumerate(zip(ax_list, object_ids, x_cents, y_cents)):
        if plot_in_bounds & (bounds != None):
            image, extent = fits_lupton(base_dir,files[object_id],
                                        bounds=[N_bound[i],S_bound[i],W_bound[i],E_bound[i]], norm_data=norm_data) 
        else:
            image, extent = fits_lupton(base_dir,files[object_id], cent=[y_cent,x_cent],
                                        img_pix=img_pix, norm_data=norm_data)
        ax.imshow(image, extent=extent)
        ax.axis('off')
        if number:
            if i % shape[0] == shape[0]-1:
                ax.text(0.68,0.78,str(n_inc),transform=ax.transAxes, rotation=270 ,color='white', fontsize=11)
                n_inc += 1
            
        if bounds != None:
            bound_box = [
                [N_bound[i],W_bound[i]],
                [N_bound[i],E_bound[i]],
                [S_bound[i],E_bound[i]],
                [S_bound[i],W_bound[i]],
                [N_bound[i],W_bound[i]]
            ]
            xb, yb = zip(*bound_box);
            ax.plot(xb, yb, color='k');
    plt.subplots_adjust(wspace=0.025,hspace=0.025)
    del fig

def plot_bound_ax(base_dir, files, object_ids, y_cents, x_cents, img_pix = 64, bounds=None, plot_in_bounds=False, norm_data=None, shape=None, number=False):
    n_obj = len(object_ids)
    n_square = np.int32(np.ceil(np.sqrt(n_obj)))
    if bounds != None: N_bound, S_bound, W_bound, E_bound = bounds
    if shape == None:
        fig, axs = plt.subplots(ncols=n_square, nrows=n_square, figsize=(8,8))
    else:
        fig, axs = plt.subplots(ncols=shape[0], nrows=shape[1], figsize=(8, 8*float(shape[1])/float(shape[0])))
    if n_square > 1:
        ax_list = axs.ravel()
    else:
        ax_list = [axs]
        
    if number:
        n_inc = 1
        
    for i, (ax, object_id, x_cent, y_cent) in enumerate(zip(ax_list, object_ids, x_cents, y_cents)):
        if plot_in_bounds & (bounds != None):
            image, extent = fits_lupton(base_dir,files[object_id],
                                        bounds=[N_bound[i],S_bound[i],W_bound[i],E_bound[i]], norm_data=norm_data) 
        else:
            image, extent = fits_lupton(base_dir,files[object_id], cent=[y_cent,x_cent],
                                        img_pix=img_pix, norm_data=norm_data)
        ax.imshow(image, extent=extent)
        ax.set_yticklabels([], fontsize=0)
        ax.set_xticklabels([], fontsize=0)
        ax.axis('off')
        #sns.despine(ax=ax, left=True, bottom=True, trim=True)
        if number:
            if i % shape[0] == shape[0]-1:
                ax.text(0.68,0.78,str(n_inc),transform=ax.transAxes, rotation=270 ,color='white', fontsize=11)
                n_inc += 1
            
        if bounds != None:
            bound_box = [
                [N_bound[i],W_bound[i]],
                [N_bound[i],E_bound[i]],
                [S_bound[i],E_bound[i]],
                [S_bound[i],W_bound[i]],
                [N_bound[i],W_bound[i]]
            ]
            xb, yb = zip(*bound_box);
            ax.plot(xb, yb, color='k');
    plt.subplots_adjust(wspace=0.025,hspace=0.025)
    #del fig
    return axs, fig
    
    
def illustrate_similarity(base_dir, files, image_id, id_test, hist_data, N_bound, S_bound, W_bound, E_bound,
                         y_cent, x_cent):
    samples_t, dist = similarity_search(hist_data, id_test, metric='cosine')
    sample_n = dist.argsort()[np.linspace(0, int(len(dist)/2.),25, dtype=np.int32)]
    plot_bound(base_dir, files, image_id[sample_n], y_cent[sample_n], x_cent[sample_n],
              bounds=[N_bound[sample_n], S_bound[sample_n], W_bound[sample_n], E_bound[sample_n]],
               plot_in_bounds=True)
    
    
def get_groups(base_dir, dir_data, output_id, obj_id, image_id, cross_match=True):
    print(base_dir+dir_data+'/model'+str(output_id)+'/conncomps/')
    group_files = glob.glob(base_dir+dir_data+'/model'+str(output_id)+'/conncomps/kmeans_classification*')
    print(group_files)
    silhouette_files = glob.glob(base_dir+dir_data+'/model'+str(output_id)+'/conncomps/kmeans_silhouette_values*')
    groupings = np.loadtxt(group_files[0], delimiter=',')
    silhouettes = np.loadtxt(silhouette_files[0], delimiter=',')
    group = np.int32(groupings[:,1])
    id_group = np.int32(groupings[:,0])
    silhouette_score = np.float32(silhouettes[:,1])
    image_id_group = []
    id_test = 0
    for i in range(len(id_group)-1):
        if id_group[i] > id_group[i+1]:
            id_test+=1
        image_id_group.append(id_test)
    image_id_group.append(id_test)
    image_id_group = np.array(image_id_group)
    if cross_match:
        groups_matched = np.zeros(len(obj_id), dtype=np.int32)-1
        silhouette_matched = np.zeros(len(obj_id), dtype=np.float32)-1
        for i in np.unique(group):
            matches, pick = cross_match_groups(i, group, obj_id, id_group, image_id, image_id_group)
            groups_matched[matches] = i
            silhouette_matched[matches] = silhouette_score[pick] # this doesn't quite work properly
        return groups_matched, silhouette_matched
    else:
        return group, id_group, image_id_group, silhouette_score

    
def cross_match_groups(group_no, group_lookup, obj_id, id_group, image_id, image_id_group):
    cross_matches = []
    pick = np.where(group_lookup == group_no)[0]
    for grp_id, img_id in zip(id_group[pick], image_id_group[pick]):
        cross = np.where((obj_id == grp_id) & (image_id == img_id))[0]
        if len(cross) == 1:
            cross_matches.append(cross[0])
        else:
            cross_matches.append(np.nan)
    cross_matches=np.array(cross_matches)
    pick = pick[np.isfinite(cross_matches)]
    cross_matches = cross_matches[np.isfinite(cross_matches)]
    return np.int64(cross_matches), pick

    
def select_tiles_HSC(fields, bands=['G', 'R', 'Z'], HSC_dir='/HSC_rerun/DM-10404/UDEEP/deepCoadd-results/'):
    i_ext = np.arange(0,9)
    j_ext = np.arange(0,9)
    files_test = []
    for field in fields:
        for i in i_ext:
            for j in j_ext:
                sub_list = []
                for band in bands:
                    s = HSC_dir+'HSC-'+band+'/'+str(field)+'/'+str(i)+'-'+str(j)+'/calexp-HSC-'\
                        +band+'-'+str(field)+'-'+str(i)+'-'+str(j)+'.fits'
                    sub_list.append(s)
                files_test.append(sub_list)
    return files_test


def output_montage(base_dir, files, img_output_dir, group_id, groups_matched, silhouette_score, image_id, N_bound, S_bound, W_bound, E_bound,
                  y_cent, x_cent):
    matches_group = np.where(groups_matched == group_id)[0]
    if not os.path.exists(img_output_dir+'group_'+str(group_id)):
        os.makedirs(img_output_dir+'group_'+str(group_id))
    for i in matches_group:
        plot_bound(base_dir, files, [image_id[i]], [y_cent[i]], [x_cent[i]],
                  bounds=[[N_bound[i]-10], [S_bound[i]+10], [W_bound[i]-10], [E_bound[i]+10]],
                 plot_in_bounds=True)
        plt.savefig(img_output_dir+'group_'+str(group_id)+'/silhouette'+str(silhouette_score[i])+'.png', bbox_inches='tight')
        plt.close()
    return group_id, len(matches_group)


def output_fits(base_dir, files, img_output_dir, group_id, groups_matched, silhouette_score, image_id, N_bound, S_bound, W_bound, E_bound,
                  y_cent, x_cent):
    bnd_names = ['G', 'R', 'I', 'Z', 'Y']
    matches_group = np.where(groups_matched == group_id)[0]
    if not os.path.exists(img_output_dir+'group_'+str(group_id)):
        os.makedirs(img_output_dir+'group_'+str(group_id))
    for i in matches_group:
        for j, b_name in enumerate(bnd_names):
            data = fits.getdata('images/'+files[image_id[i]][j])
            data_cut = data[N_bound[i]-10:S_bound[i]+10,W_bound[i]-10:E_bound[i]+10]
            if data_cut.size > 10:
                hdu = fits.PrimaryHDU()
                hdu.data = data_cut
                hdu.writeto(img_output_dir+'group_'+str(group_id)+'/'+b_name+'_'+str(i)+'_'+str(silhouette_score[i])+'.fits', overwrite=True)
    return group_id, len(matches_group)


def html_montage(img_output_dir):
    table = '<html><head></head><body><h1>Min galaxy size: 20</h1>'
    folders = glob.glob(img_output_dir+'/group*')
    for folder in folders:
        m = re.split('_', folder)
        group = m[-1]
        files = glob.glob(folder+'/*')
        score = np.array([])
        file_lst = np.array([])
        for file in files:
            m = re.split('/', file)
            file_lst = np.append(file_lst,'group_'+group+'/'+m[-1])
            m = re.split('[e_,.]', file)
            try:
                score = np.append(score, np.float32(m[-3]+'.'+m[-2]))
            except:
                score = np.append(score, np.float32(-1))
        objs = np.argsort(score)[::-1]
        print(score[np.argsort(score)[::-1]])
        table += '<div style="clear:both;"><h2>Cluster {0}:</h2>'.format(group)
        itt = 0
        for obj in objs:
            gal_score = score[obj]
            file = files[obj]
            table += "<div id='thumbnail' style='float:left; font-size: 10px;'>\r\n<table><tr><td>\r\n"
            table += '<img src="{0}" alt="{1}" style="margin:1px;float:left;"></img>\r\n</td></tr><tr><td align="middle">\r\n<span style="font-size: 14px;">'.format(file_lst[obj], 1)
            table += '{0}</span>\r\n</td></tr></table>\r\n</div>\r\n'.format(gal_score)
            itt += 1
            if itt > 15:
                break
        table += '</div>'
    table += '</body></html>'
    file = open(img_output_dir + '/index.html', 'w')
    file.write(table)
    file.close()
    return None


def get_good_tiles_HSC(base_dir, files_to_check, verbose=False):
    bounds = []
    files = files_to_check[:]
    for i, tile in enumerate(files_to_check):
        try:
            if glob.glob(base_dir+'/images'+tile[1]) != []:
                image_data = fits.getdata(base_dir+'/images'+tile[1])
                good_mask = auto_detect_good(image_data, min_counts=20000., data_min=0., data_max=0.05)
                if (np.count_nonzero(good_mask) > np.count_nonzero(~good_mask)*4) & (np.std(image_data) > 0.02):
                    bounds.append([0,image_data.shape[0],0,image_data.shape[1]])
                    if verbose:
                        dummy = re.findall('/calexp*.*fits', tile[1])[0]
                        dummy = re.split('[.,-]', dummy)
                        print(dummy[3], ',', dummy[4], '-', dummy[5], 'OK')
                else:
                    if verbose:
                        dummy = re.findall('/calexp*.*fits', tile[1])[0]
                        dummy = re.split('[.,-]', dummy)
                        print(dummy[3], ',', dummy[4], '-', dummy[5], 'is bad')
                    files[i] = -100
                    bounds.append(-100)
                del image_data
            else:
                if verbose:
                    dummy = re.findall('/calexp*.*fits', tile[1])[0]
                    dummy = re.split('[.,-]', dummy)
                    print(dummy[3], ',', dummy[4], '-', dummy[5], 'does not exist')
                files[i] = -100
                bounds.append(-100)
        except IOError:
            if verbose:
                dummy = re.findall('/calexp*.*fits', tile[1])[0]
                dummy = re.split('[.,-]', dummy)
                print(dummy[3], ',', dummy[4], '-', dummy[5], 'IO error')
            files[i] = -100
            bounds.append(-100)
            pass 
    files = filter(lambda a: a != -100, files);
    bounds = filter(lambda a: a != -100, bounds);
    return files, bounds

def bulk_rename(folder):
    files = glob.glob(folder+'/*')
    for file in files:
        if ',' in file:
            new_file = [char if char != ',' else '-' for char in file]
            new_file = ''.join(new_file)
            print(file + '-->' + new_file)
            os.system('mv '+file+' '+new_file)
