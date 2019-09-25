import glob
from graph_clustering import run_classify, bulk_rename
import os

# Edit these!
#========================================================
HSC_password = ''
HSC_user = ''
#========================================================

dir_data = 'HSC_example'
dir_base = '.'
output_id = 1
patch_folder = 'ps'
patch_size = 10
nodes = 15000
iterations=150000
clusters = 800
threads = 14
n_samples = 500000
metric = 'pspearson'
bands = ['G','R','I']
bounds = [[0,4200,0,4200],[0,4200,0,4200],[0,4200,0,4200],[0,4200,0,4200]]
files = [['calexp-HSC-G-8767-3-2.fits',
          'calexp-HSC-R-8767-3-2.fits',
          'calexp-HSC-I-8767-3-2.fits'],
         ['calexp-HSC-G-8767-4-2.fits',
          'calexp-HSC-R-8767-4-2.fits',
          'calexp-HSC-I-8767-4-2.fits'],
         ['calexp-HSC-G-8767-5-2.fits',
          'calexp-HSC-R-8767-5-2.fits',
          'calexp-HSC-I-8767-5-2.fits'],
         ['calexp-HSC-G-8767-6-2.fits',
          'calexp-HSC-R-8767-6-2.fits',
          'calexp-HSC-I-8767-6-2.fits']]

# Download image files (requires HSC account from https://hsc-release.mtk.nao.ac.jp/doc/)

if glob.glob(dir_base+'/images') == []:
    os.mkdir(dir_base+'/images')
    os.system('wget --password '+HSC_password+' --user '+HSC_user+' -i urls -P '+\
             dir_base+'/images/')
    bulk_rename(dir_base+'/images')



# Run classification

run_classify(dir_base=dir_base, dir_data=dir_data, files=files, bounds=bounds,
             bands=bands, output_id=output_id, patch_folder=patch_folder,
             patch_size=patch_size, nodes=nodes, clustering_target=clusters,
             threads=threads, metric=metric, n_samples=n_samples,
             iterations=iterations,
             patch_extraction=True,
             parallel_extract=True,
             GNG_model=True,
             hierarchical_clustering=True,
             connected_components=True,
             group_train=True,
             make_montage=True,
             k=70)
