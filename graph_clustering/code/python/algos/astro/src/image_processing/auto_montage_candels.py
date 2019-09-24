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


def PIL2array(img):
    return numpy.array(img.getdata(),
                    numpy.uint8).reshape(img.size[1], img.size[0], 3)

def array2PIL(arr, size):
    mode = 'RGBA'
    arr = arr.reshape(arr.shape[0]*arr.shape[1], arr.shape[2])
    if len(arr[0]) == 3:
        arr = numpy.c_[arr, 255*numpy.ones((len(arr),1), numpy.uint8)]
    return Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)

Field = collections.namedtuple('Field', 'id name fits_file shape offset')
fields = {}

fields[0] = Field(0, 'goodsn', '/goodsn/hlsp_candels_hst_wfc3_gn-tot-60mas_f160w_v1.0_drz.fits', [20480, 20480], [0, 0])
fields[1] = Field(1, 'uds', 'hlsp_candels_hst_wfc3_uds-tot_f160w_v1.0_drz.fits', [12800, 30720], [0, 0])
fields[2] = Field(2, 'egs', 'hlsp_candels_hst_wfc3_egs-tot-60mas_f160w_v1.0_drz.fits', [12600, 40800], [0, 0])
fields[3] = Field(3, 'cos', 'hlsp_candels_hst_wfc3_cos-tot_f160w_v1.0_drz.fits', [36000, 14000], [0, 0])
fields[4] = Field(4, 'goodss', '/goodss/hlsp_candels_hst_wfc3_gs-tot_f160w_v1.0_drz.fits', [16500, 15300], [12000, 28500, 7000, 22300]) #[40500, 32400]
fits_image_folder = 'J:/kdata/candels/'


def output_catalogue_cutouts_final_cat(field_id, field_key, image_folder_path, catalogue_path, output_path,
                                       sky_areas_input, hoffset, sky_area_id, class_index, galaxy_count=0,
                                       cont_count=0):

    field_obj = fields[field_id]

    fits_file_path = fits_image_folder + field_obj.fits_file
    hdulist = pyfits.open(fits_file_path)
    w = wcs.WCS(hdulist[0].header)
    hdulist.close()

    complete_cat = numpy.loadtxt(catalogue_path, delimiter=',')

    y_field_offset = field_offsets[field_key][0]
    x_field_offset = field_offsets[field_key][1]

    folder_names = []
    for row_idx in range(sky_areas_input.shape[0]):
        field = sky_areas_input.field[row_idx].strip()
        image = Image.open(image_folder_path)
        image = numpy.array(image)

        #0,91166,12552,1589,189.149867,62.094358,3,12537.001,1584.393,189.150401,62.094282,19,19,19,9,59,59,59,59,59,0.56253,0.56253,0.56253,0.56253,0.53228,0.53228,0.53228,0.53228,0.53228
        cat = complete_cat[complete_cat[:, 0] == sky_area_id][:, 1:]

        for i in range(cat.shape[0]):

            galaxy = cat[i, :]

            num_patches = galaxy[0]
            wh = galaxy[1]
            if num_patches < 3:  # 12
                cont_count += 1
                continue

            galaxy_count += 1
            # objid numpatches width height     cleft cright ctop cbottom   cx cy bleft bright btop bbottom
            obj_id = int(galaxy[7])

            cat_ra = galaxy[5]
            cat_dec = galaxy[6]

            s_ra = galaxy[10]
            s_dec = galaxy[11]

            obj_x = galaxy[8]
            obj_y = galaxy[9]
            if sky_area_id == 2 or sky_area_id == 4: # egs is wonky x y, so is goods south
                obj_x = galaxy[3]
                obj_y = galaxy[4]

            #world = w.wcs_pix2world([[obj_x, obj_y]], 1)  #x first y second
            #pixcrd_cat = w.wcs_world2pix(world, 1)

            pixcrd2 = w.wcs_world2pix([[s_ra, s_dec]], 1).astype(numpy.int)
            obj_x = pixcrd2[0][0]
            obj_y = pixcrd2[0][1]

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

            #field_sizes = { 'gn' : [20480, 20480], 'gs' : [40500, 32400], 'egs' : [12600, 40800], 'cos' : [36000, 14000], 'uds' : [12800, 30720]}
            #field_offsets = {'gn' : [0,0], 'gs' : [16400, 10200], 'egs' : [0,0], 'cos' : [0, 0], 'uds':[0,0]}

            y_top = hoffset - (b - y_field_offset)
            y_bottom = hoffset - (t - y_field_offset)

            x_left = l - x_field_offset
            x_right = r  - x_field_offset

            if x_right > image.shape[1] -1 or y_top > image.shape[0] - 1:
                print("skipping: {} as outside image, {}".format(x_right, y_top))
                continue
            if x_left < 0:
                print("skipping: {} as outside image -ve, {}".format(x_left, y_bottom))
                continue
            #clip = image[hoffset-t:hoffset-b, l:r]
            clip = image[y_bottom:y_top, x_left:x_right]
            #print galaxy

            type_row = galaxy[12:32]#[12:24]#[12:24]#[12:23] #[12:21]
            prox_row = galaxy[32:]#[24:]#[24:]#[23:] #[21:]
            #print type_row
            #print prox_row
            #print galaxy
            #print type_row
            #print prox_row

            type = int(type_row[class_index])
            prox = str(prox_row[class_index])

            if prox.startswith("-"):
                prox = prox.replace("-", "minus")
            else:
                prox = "plus" + prox
            prox = prox.replace(".", "dot")
            print ("{0} type/cluster: {1} sil score: {2}".format(type_row, type, prox))


            output_folder = output_path + '/{0}'.format(type)
            if not os.path.isdir(output_folder):
                print ("creating folder: {0}".format(type))
                os.mkdir(output_folder)

            output_cutout_name = output_folder + '/galaxy_{0}_{1}_{2}_{3}_{4}.png'.format(sky_area_id, type, obj_id, prox, field_code[sky_area_id])

            img2 = Image.fromarray(clip)
            img2.save(output_cutout_name)

    print("continue count: {0}".format(cont_count))
    print("galaxy count: {}".format(galaxy_count))
    return galaxy_count, cont_count

def output_catalogue_cutouts(image_folder_path, catalogue_path, gal_types_path, output_path, sil_path, sky_areas_input,
                             hoffset, sky_area_id):

    # load catalogue of all objects over 40 patches
    complete_cat = numpy.loadtxt(catalogue_path, dtype=numpy.int, delimiter=' ')
    complete_types = numpy.loadtxt(gal_types_path, dtype=numpy.int, delimiter=',')
    complete_sil_score = numpy.loadtxt(sil_path, delimiter=',')

    current_sky_area = -1
    sky_area_folder = '/0/'

    folder_names = []
    for row_idx in range(sky_areas_input.shape[0]):

        #sky_area_id = sky_areas_input.id[row_idx]
        field = sky_areas_input.field[row_idx].strip()

        # load sky_area image
        #sky_area_folder = '/'+ str(field) + '/'
        image = Image.open(image_folder_path)
        image = numpy.array(image)

        # get sky area catalogue
        cat = complete_cat[complete_cat[:,0] == sky_area_id][:, 2:]
        types = complete_types[complete_types[:, 0] == sky_area_id][:, 2:]
        sil_score = complete_sil_score[complete_sil_score[:, 0] == sky_area_id][:, 2:]

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
            clip = image[hoffset-t:hoffset-b, l:r]
            #clip = image[b:t, l:r]

            type_row = types[types[:, 0] == obj_id]
            if type_row is None or len(type_row) == 0:
                print ("type row none: {0}".format(obj_id))
                continue


            #type = str(type_row[0][1])
            type= str(type_row[0][9])
            sub_type = 'blah'
            if len(type_row[0]) == 3:
                sub_type = str(type_row[0][2])

            sil_val = sil_score[sil_score[:, 0] == obj_id]

            sil_val = str(sil_val[0][9])
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

field_code = { 0: 'gn', 1 : 'uds', 2:'egs',3:'cos', 4:'gs'}
field_image = { 0: 'goodsn.png', 1: 'uds.png', 2:'egs.png', 3:'cos.png', 4:'gs_160_814_606.png'}
#field_sizes = { 'gn' : [20480, 20480], 'gs' : [40500, 32400], 'egs' : [12600, 40800], 'cos' : [36000, 14000], 'uds' : [12800, 30720]}
field_sizes = { 'gn' : [20480, 20480], 'gs' : [16500, 32400], 'egs' : [12600, 40800], 'cos' : [36000, 14000], 'uds' : [12800, 30720]}
field_offsets = {'gn' : [0,0], 'gs' : [12000, 7000], 'egs' : [0,0], 'cos' : [0, 0], 'uds':[0,0]}


def process_final(root_folder, test_folder, output_path, image_folder_path, catalog_path):

    class_index = 19

    gal_count = 0
    cont_count = 0
    for sky_area_id in [0]: #range(5): # not yet goods south

        field_key = field_code[sky_area_id]
        hoffset = field_sizes[field_key][0]

        image_file_path = image_folder_path + field_image[sky_area_id]

        sky_area_file_name = root_folder + 'sky_areas_{0}.txt'.format(sky_area_id)
        print (sky_area_file_name)
        sky_areas_input = pd.read_csv(sky_area_file_name, sep=',')

        folder_name = 'labels_{}_1000_1000'.format(class_index)
        label_output_path = os.path.join(output_path, folder_name)
        print (label_output_path)
        if not os.path.isdir(output_path):
            print ("creating folder: {0}".format(output_path))
            os.mkdir(output_path)
        if not os.path.isdir(label_output_path):
            print ("creating folder: {0}".format(label_output_path))
            os.mkdir(label_output_path)

        gal_count, cont_count = output_catalogue_cutouts_final_cat(field_id=sky_area_id, field_key=field_key,
            image_folder_path=image_file_path, catalogue_path=catalog_path,
            output_path=label_output_path, sky_areas_input=sky_areas_input, hoffset=hoffset,
            sky_area_id=int(sky_area_id), class_index=class_index, galaxy_count=gal_count, cont_count=cont_count)

        #break
    print("galaxy_count: {}  cont_count: {}".format(gal_count, cont_count))

def process(root_folder, sky_area_id, test_folder, output_path, image_folder_path, catalog_path, hoffset):

    clus_type='agg'

    # id, field, field_rect, sigma_patch
    sky_area_file_name = root_folder + 'sky_areas_{0}.txt'.format(sky_area_id)
    print (sky_area_file_name)
    sky_areas_input = pd.read_csv(sky_area_file_name, sep=',')

    label_files = filter(lambda x: x.startswith(clus_type + '_classifications_labels'), os.listdir(test_folder))
    for label_file in label_files:
        m = re.match('(kmeans|agg)_classifications_labels_([0-9]+)_([0-9]+)_([0-9]+).txt', label_file)
        if m == None:
            print ("skipping file: {0}".format(label_file))
            continue
        numk = m.group(2)
        minpixels = m.group(3)
        num_roots = m.group(4)
        sil_path = test_folder + '/' +clus_type + '_silhouette_values_{0}_{1}_{2}.txt'.format(
            int(numk), int(minpixels), int(num_roots))
        folder_name = 'labels_{0}_{1}_{2}'.format(numk, minpixels, num_roots)
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

    root_folder = 'f:/kdata/candels3/twocolor/'
    test_folder = root_folder + 'model_all_4/catalogs'
    output_path = 'e:/candels/output_ml_ref/' #test_folder + '/output_cat_test/'
    catalog_path = test_folder + '/final_catalogue_debug.csv'
    root_img_folder = 'f:/kdata/candels/'

    process_final(root_folder, test_folder, output_path, root_img_folder, catalog_path)



def main2():

    root_folder = 'E:/kdata/candels4/twocolor/'
    test_folder = root_folder + 'model_all/'
    agglom_path = test_folder+ '/output/galaxy_train/'

    catalog_path = test_folder + '/complete_object_catalogue_ps_egs_all.txt'
    output_path = agglom_path
    image_folder_path = 'E:/kdata/candels1/egs.png'
    hoffset = field_sizes['egs'][0]
    sky_area_id = 2
    print (hoffset)

    #process(root_folder, sky_area_id, test_folder, output_path, image_folder_path, catalog_path, hoffset)

    root_img_folder = 'E:/kdata/candels/'

    process(root_folder, 0, test_folder, output_path,
            root_img_folder + 'goodsn.png',
            test_folder + '/complete_object_catalogue_ps_goodsn_all.txt',
            field_sizes['gn'][0])

    process(root_folder, 1, test_folder, output_path,
            root_img_folder + 'uds.png',
            test_folder + '/complete_object_catalogue_ps_uds_all.txt',
            field_sizes['uds'][0])

    process(root_folder, 2, test_folder, output_path,
            root_img_folder + 'egs.png',
            test_folder + '/complete_object_catalogue_ps_egs_all.txt',
            field_sizes['egs'][0])

    process(root_folder, 3, test_folder, output_path,
            root_img_folder + 'cos.png',
            test_folder + '/complete_object_catalogue_ps_cos_all.txt',
            field_sizes['cos'][0])

    process(root_folder, 4, test_folder, output_path,
            root_img_folder + 'goodss.png',
            test_folder + '/complete_object_catalogue_ps_goodss_all.txt',
            field_sizes['gs'][0])


if __name__ == '__main__':
    main()


print ("end")