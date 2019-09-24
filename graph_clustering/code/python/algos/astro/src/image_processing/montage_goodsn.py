import os
import numpy
import matplotlib.image as mplim
from PIL import Image
import re
import pandas as pd
from astropy import wcs
from astropy.io import fits as pyfits
from astropy import units as u
from astropy.coordinates import SkyCoord
import collections

field_code = { 0: 'gn', 1 : 'uds', 2:'egs',3:'cos', 4:'gs'}
field_image = { 0: 'goodsn.png', 1: 'uds.png', 2:'egs.png', 3:'cos.png', 4:'gs_160_814_606.png'}
#field_sizes = { 'gn' : [20480, 20480], 'gs' : [40500, 32400], 'egs' : [12600, 40800], 'cos' : [36000, 14000], 'uds' : [12800, 30720]}
field_sizes = { 'gn' : [20480, 20480], 'gs' : [16500, 32400], 'egs' : [12600, 40800], 'cos' : [36000, 14000], 'uds' : [12800, 30720]}
field_offsets = {'gn' : [0,0], 'gs' : [12000, 7000], 'egs' : [0,0], 'cos' : [0, 0], 'uds':[0,0]}


def output_catalogue_cutouts(image_folder_path, catalogue_path, gal_types_path, output_path, sil_path, sky_areas_input,
                             hoffset, sky_area_id):

    # load catalogue of all objects over 40 patches
    complete_cat = numpy.loadtxt(catalogue_path, dtype=numpy.int, delimiter=',')
    complete_types = numpy.loadtxt(gal_types_path, dtype=numpy.int, delimiter=',')
    complete_sil_score = numpy.loadtxt(sil_path, delimiter=',')

    current_sky_area = -1
    sky_area_folder = '/0/'

    folder_names = []
    for row_idx in range(sky_areas_input.shape[0]):

        #sky_area_id = sky_areas_input.id[row_idx]
        #field = sky_areas_input.field[row_idx].strip()

        # load sky_area image
        #sky_area_folder = '/'+ str(field) + '/'
        Image.MAX_IMAGE_PIXELS = None
        image = Image.open(image_folder_path)
        image = numpy.array(image)

        # get sky area catalogue
        cat = complete_cat# [complete_cat[:,0] == sky_area_id][:, 2:]
        types = complete_types #[complete_types[:, 0] == sky_area_id][:, 2:]
        sil_score = complete_sil_score #[complete_sil_score[:, 0] == sky_area_id][:, 2:]

        cont_count = 0
        for i in range(cat.shape[0]):

            galaxy = cat[i, :]

            # objid numpatches width height     cleft cright ctop cbottom   cx cy bleft bright btop bbottom
            obj_id = galaxy[0]
            numpatches = galaxy[1]

            if numpatches < 2:
                cont_count += 1
                continue

            width = galaxy[2]
            height = galaxy[3]
            co_left = galaxy[4]
            co_right = galaxy[5]
            co_top = galaxy[6]
            co_bottom = galaxy[7]

            obj_x = galaxy[8]
            obj_y = galaxy[9]



            br_left = galaxy[10]
            br_right = galaxy[11]
            br_top = galaxy[12]
            br_bottom = galaxy[13]
            if (br_right - br_left < 5) and (br_bottom - br_top < 5):
                continue

            size = 100
            diff = 100/2
            # calc
            l = obj_x - diff
            r = obj_x + diff
            if r-l < size:
                r += (size-(r-l))

            t = obj_y + diff
            b = obj_y - diff
            if t-b < size:
                t += (size-(t-b))

            #t -= 16400
            #b -= 16400
            #l -= 10200
            #r -= 10200
            #left=10200
            #right=19500
            #bottom=16400
            #top=25500
            #if l < 0 or r > 9300:
            #    print "outside width: l {0} r {1}".format(l, r)
            #    continue
            #if t > 9099 or b < 0:
            #    print "outside height: b {0} t {1}".format(b, t)
            #    continue
            #if l < 0:
            #    l = 0
            #if b < 0:
            #    b = 0
            #if t >= 9100:
            #    t = 9099
            #if r >= 9300:
            #    r = 9299

            # goods north 20480 by 20480
            # goods south 9100 9100
            # egs 40800 12600
            #hoffset = 12600
            #print "hoffset: {0} t: {1} b: {2} l: {3} r: {4}".format(hoffset, t, b, l, r)
            #print "image shape: {0} {1}".format(image.shape[0], image.shape[1])
            #print "hoffset - t: {0} hoffset - b: {1}".format(hoffset-t, hoffset-b)
            clip = image[int(hoffset-t):int(hoffset-b), int(l):int(r)]
            #clip = image[b:t, l:r]

            type_row = types[types[:, 0] == obj_id]
            if type_row is None or len(type_row) == 0:
                print ("type row none: {0}".format(obj_id))
                continue


            #type = str(type_row[0][1])
            type = str(type_row[0][1])

            sil_val = sil_score[sil_score[:, 0] == obj_id]

            sil_val = str(sil_val[0][1])
            if sil_val.startswith("-"):
                sil_val = sil_val.replace("-", "minus")
            else:
                sil_val = "plus" + sil_val
            sil_val = sil_val.replace(".", "dot")
            print ("{0} type/cluster: {1} sil score: {2}".format(type_row, type, sil_val))

            output_folder = output_path + '/{0}'.format(type)
            if not os.path.isdir(output_folder):
                print ("creating folder: {0}".format(type))
                os.mkdir(output_folder)

            #subtype_output_folder = output_folder + '/' + sub_type
            #if not os.path.isdir(subtype_output_folder):
            #    print "creating folder: {0}".format(sub_type)
            #    os.mkdir(subtype_output_folder)

            #output_cutout_name = output_folder + '/' + sub_type + '/galaxy_{0}_{1}_{2}_{3}_u.png'.format(sky_area_id, type, obj_id, sil_val)
            output_cutout_name = output_folder + '/galaxy_{0}_{1}_{2}_{3}_{4}.png'.format(sky_area_id, type, obj_id, sil_val, field_code[sky_area_id])
            #print(clip)
            img2 = Image.fromarray(clip)
            img2.save(output_cutout_name)

        print("continue count: {0}".format(cont_count))

def process(root_folder, sky_area_id, test_folder, output_path, image_folder_path, catalog_path, hoffset, clus_type):

    # id, field, field_rect, sigma_patch
    #sky_area_file_name = root_folder + 'sky_areas_{0}.txt'.format(sky_area_id)
    #print (sky_area_file_name)
    #sky_areas_input = pd.read_csv(sky_area_file_name, sep=',')
    sky_areas_input = numpy.array([0])

    label_files = filter(lambda x: x.startswith(clus_type + '_classifications_labels'), os.listdir(test_folder))
    for label_file in label_files:
        #m = re.match('(kmeans|agg)_classifications_labels_([0-9]+)_([0-9]+)_([0-9]+).txt', label_file)
        m = re.match('(kmeans|agg)_classifications_labels_([0-9]+)_([0-9]+).txt', label_file)
        if m == None:
            print ("skipping file: {0}".format(label_file))
            continue

        algo = m.group(1)
        numk = m.group(2)
        minpixels = m.group(3)
        num_roots = 0 #m.group(4)
        sil_path = test_folder + '/' +clus_type + '_silhouette_values_{0}_{1}.txt'.format(
            int(numk), int(minpixels)) #, int(num_roots)
        folder_name = 'labels_{0}_{1}_{2}_{3}'.format(numk, minpixels, num_roots, algo)
        label_output_path = os.path.join(output_path, folder_name)
        print (label_output_path)
        if not os.path.isdir(output_path):
            print ("creating folder: {0}".format(output_path))
            os.mkdir(output_path)
        if not os.path.isdir(label_output_path):
            print ("creating folder: {0}".format(label_output_path))
            os.mkdir(label_output_path)

        label_input_file_path = os.path.join(test_folder, label_file)
        print ("{0} {1}".format(label_output_path, label_input_file_path))
        output_catalogue_cutouts(
            image_folder_path=image_folder_path, catalogue_path=catalog_path,
            gal_types_path=label_input_file_path, output_path=label_output_path,
            sil_path=sil_path, sky_areas_input=sky_areas_input, hoffset=hoffset, sky_area_id=int(sky_area_id))



def main():
    root_folder = '/data/ryanjackson/candels2/'
    root_img_folder = root_folder + '/images/'
    test_folder = root_folder + 'tests/'
    counts_folder = test_folder+ '/model0/conncomps/'
    catalog_path = counts_folder + '/object_catalogue_1210_cosine_ps_0_1.txt'
    output_path = counts_folder
    hoffset = field_sizes['gn'][0]
    print (hoffset)

    clus_type='kmeans'  # agg


    process(test_folder, 0, counts_folder, output_path,
            root_img_folder + 'goodsn.png',
            catalog_path,
            field_sizes['gn'][0],
            clus_type)


if __name__ == '__main__':
    main()
