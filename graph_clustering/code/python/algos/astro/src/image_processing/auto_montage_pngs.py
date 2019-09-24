import os
import numpy
import matplotlib.image as mplim
from PIL import Image
import re
import pandas as pd

def PIL2array(img):
    return numpy.array(img.getdata(),
                    numpy.uint8).reshape(img.size[1], img.size[0], 3)

def array2PIL(arr, size):
    mode = 'RGBA'
    arr = arr.reshape(arr.shape[0]*arr.shape[1], arr.shape[2])
    if len(arr[0]) == 3:
        arr = numpy.c_[arr, 255*numpy.ones((len(arr),1), numpy.uint8)]
    return Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)

def output_catalogue_cutouts(image_folder_path, catalogue_path, gal_types_path, output_path, sil_path, sky_areas_input):

    # load catalogue of all objects over 40 patches
    complete_cat = numpy.loadtxt(catalogue_path, dtype=numpy.int, delimiter=' ')
    complete_types = numpy.loadtxt(gal_types_path, dtype=numpy.int, delimiter=',')
    complete_sil_score = numpy.loadtxt(sil_path, delimiter=',')

    current_sky_area = -1
    sky_area_folder = '/0/'

    folder_names = []
    for row_idx in range(sky_areas_input.shape[0]):

        sky_area_id = sky_areas_input.id[row_idx]
        field = sky_areas_input.field[row_idx].strip()

        # load sky_area image
        sky_area_folder = '/'+ str(field) + '/'
        image = Image.open(image_folder_path + sky_area_folder + 'image.png')
        image = numpy.array(image)

        # get sky area catalogue
        cat = complete_cat[complete_cat[:,1] == sky_area_id][:, 2:]
        types = complete_types[complete_types[:, 1] == sky_area_id][:, 2:]
        sil_score = complete_sil_score[complete_sil_score[:, 1] == sky_area_id][:, 2:]

        for i in range(cat.shape[0]):

            galaxy = cat[i, :]

            # objid numpatches width height     cleft cright ctop cbottom   cx cy bleft bright btop bbottom
            obj_id = galaxy[0]
            numpatches = galaxy[1]
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

            if l < 0:
                l=0
            if b < 0:
                b=0
            if t > 3599:
                t = 3599
            if r > 3599:
                r = 3599

            clip = image[3600-t:3600-b, l:r]
            #clip = image[b:t, l:r]

            type_row = types[types[:, 0] == obj_id]
            if type_row is None or len(type_row) == 0:
                print ("type row none: {0}".format(obj_id))
                continue


            type = str(type_row[0][1])
            sub_type = 'blah'
            if len(type_row[0]) == 3:
                sub_type = str(type_row[0][2])

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

            subtype_output_folder = output_folder + '/' + sub_type
            if not os.path.isdir(subtype_output_folder):
                print ("creating folder: {0}".format(sub_type))
                os.mkdir(subtype_output_folder)

            output_cutout_name = output_folder + '/' + sub_type + '/galaxy_{0}_{1}_{2}_{3}.png'.format(sky_area_id, type, obj_id, sil_val)
            img2 = Image.fromarray(clip)
            img2.save(output_cutout_name)


def main():

    root_folder = 'K:/DECaLS/'
    test_folder = root_folder + 'test_all/'
    agglom_path = test_folder+ '/output_0/model_all/pspearson243/galaxy_train/'
    catalog_path = test_folder + '/output_0/model_all/complete_object_catalogue_ps_243_4_1_s1.txt'
    output_path = agglom_path + 'cutouts/'
    image_folder_path = root_folder + 'data/jim/DECaLS/243/'
    #image_path = base_path + 'image.png'

    # id, field, field_rect, sigma_patch
    sky_areas_input = pd.read_csv(root_folder + 'sky_areas_243.txt', sep=',')

    #classifications = agglom_path + 'kmeans_classifications2.txt'

    label_files = filter(lambda x: x.startswith('kmeans_classifications_labels'), os.listdir(agglom_path))
    for label_file in label_files:
        m = re.match('kmeans_classifications_labels_([0-9]+)_([0-9]+).txt', label_file)
        if m == None:
            print ("skipping file: {0}".format(label_file))
            continue
        numk = m.group(1)
        minpixels = m.group(2)
        sil_path = agglom_path + '/silhouette_values_{0}_{1}.txt'.format(int(numk), int(minpixels))
        folder_name = 'labels_{0}_{1}'.format(numk, minpixels)
        label_output_path = os.path.join(output_path, folder_name)
        print (label_output_path)
        if not os.path.isdir(output_path):
            print ("creating folder: {0}".format(output_path))
            os.mkdir(output_path)
        if not os.path.isdir(label_output_path):
            print ("creating folder: {0}".format(label_output_path))
            os.mkdir(label_output_path)

        label_input_file_path = os.path.join(agglom_path, label_file)
        print ("{0} {1}".format(label_output_path, label_input_file_path))
        output_catalogue_cutouts(
            image_folder_path=image_folder_path, catalogue_path=catalog_path,
            gal_types_path=label_input_file_path, output_path=label_output_path,
            sil_path=sil_path, sky_areas_input=sky_areas_input)

def main3():
    #image_path = 'k:/users/abell2744_cb.png'
    image_path = 'k:/users/stiff_macs0416.png'
    #output_path = 'c:/users/ah14aeb/projects/mnras2/'
    output_path = 'k:/software/mnras2_images_stiff/'
    get_big_cutout(image_path, output_path)

def get_big_cutout(image_path, output_path):

    # big macs0416(from config)
    left=2110
    right=7370
    top=7200 #10000-2800
    bottom=2790 # 10000-7210

    # big abell2744
    #left=3405
    #right=6550
    #top=8505#top=8249        # 12300-4051
    #bottom=4051#bottom=3795     # 12300-8505

    image = Image.open(image_path)
    image = numpy.array(image)
    #clip = image[10000-t:10000-b, l:r]
    clip = image[bottom:top, left:right]
    #output_cutout_name = output_path + '/big_cut_out_macs_cb.png'
    #img2 = Image.fromarray(clip)
    #img2.save(output_cutout_name)

    # create posh background and edge
    x, y, z = clip.shape
    border_width = 6
    width =  x + (border_width * 2)
    height = y + (border_width * 2)
    posh = numpy.zeros((width, height, z), dtype=numpy.uint8)

    # make white
    posh[:] = 255

    # make grey two pixel border
    offset = border_width - 4
    posh[offset:width-offset, offset:height-offset, :] = numpy.array([164,164,164])

    # make black two pixel border
    offset = border_width - 2
    posh[offset:width-offset, offset:height-offset, :] = numpy.array([0,0,0])

    # copy clip into posh
    offset = border_width
    posh[offset:offset+x, offset:y+offset, :] = clip

    img2 = Image.fromarray(posh)
    img2.save(output_path + '/posh_macs0416_cb.png')


if __name__ == '__main__':
    main()
