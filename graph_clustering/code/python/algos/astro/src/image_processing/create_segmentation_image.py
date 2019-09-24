__author__ = 'ah14aeb'
import os
import sys
from astro.utility import astro_config
from astropy.io import fits as pyfits
import numpy as np
from PIL import Image
from astro.mlhelper import cluster_helper
import matplotlib.pyplot as plt


class SegImage(object):

    def __init__(self, output_folder_path, rect, width, height, num_clusters, test_num, label_manager):
        self.rect = rect
        self.width = width
        self.height = height
        self._num_clusters = num_clusters
        self.output_folder_path = output_folder_path
        self.test_number = test_num
        self.label_manager = label_manager

    def __get_cluster_list_by_size(self, datapoint_cluster_index, max_clusters):
        cluster_size_list = cluster_helper.get_cluster_size_list(datapoint_cluster_index)
        # Descending order - largest first - smallest last
        cluster_size_list = cluster_helper.sort_array(cluster_size_list, 1, False)
        print "number of clusters: {0}".format(cluster_size_list.shape[0])
        print "number of clusters smaller than 10: {0}".format(cluster_size_list[cluster_size_list < 11].shape[0])
        print "cluster size list {0}".format(cluster_size_list)


        num_clusters = cluster_size_list.shape[0]

        clusters_to_display = num_clusters
        if self._num_clusters > 0:
            clusters_to_display = min(num_clusters, max_clusters)

        return cluster_size_list, num_clusters, clusters_to_display

    def __colour_samples(self,
                         img, fits_img, positions, datapoint_cluster_index,
                         window_size, intermediates=np.array([]),
                         output_singles=False):

        cluster_size_list, num_clusters, clusters_to_display = \
            self.__get_cluster_list_by_size(datapoint_cluster_index, self._num_clusters)

        cluster_accept_list = np.array([  45,491,819,822,738,265,136,264,420,537,565,93,827,526,693,525,302,146,91,663,358,524,128,371,631,823,354,522,527,542,297,726,308,14,472,535,40,759,714,367,643])
        cluster_remove_list = np.array([18108,5723,2662,1264,6389,2753,13494, 919, 1108, 2716])
        # loop through the clusters starting with the largest
        cluster_counter = 0
        for i in range(clusters_to_display):
            #if i > 40:
            #    break
            #if i < 4 or i == 6:
            #    continue
            cluster_index = cluster_size_list[i][0]

            #if cluster_index in cluster_remove_list:
            #   continue
            #if cluster_accept_list[cluster_accept_list == cluster_index].shape[0] == 0:
            #    continue

            cluster_mask = datapoint_cluster_index[:,1] == cluster_index
            cluster_datapoints = datapoint_cluster_index[cluster_mask]
            cluster_positions = positions[cluster_mask]

            timg = None
            if output_singles:
                # create new image
                timg = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                timg[:,:] = [255, 255, 255]# [235, 255, 127] # set background to white

            self.__write_cluster_to_images(img, timg, fits_img, cluster_datapoints, cluster_index,
                                           cluster_positions, window_size, output_singles, i)

            cluster_counter += 1

            if output_singles and cluster_datapoints.shape[0] > 20:
                print "outputting image of cluster: {0} {1}".format(cluster_counter, cluster_index)
                timg_out = self.__get_sub_image(timg)
                timg_out.save(self.output_folder_path + 'output_cluster_image_' + str(cluster_counter - 1) + '-' + str(cluster_index) + '.png')

            if cluster_counter in intermediates:
                print "outputting image: {0}".format(cluster_counter)
                img_out = self.__get_sub_image(img) #Image.fromarray(img)
                img_out.save(self.output_folder_path + 'output_seg_image_' + str(cluster_counter) + '.png')

    def __write_cluster_to_images(self,
                img, timg, fits_img, cluster_datapoints, cluster_index, cluster_positions, window_size, output_singles, i):

        for sample_idx in range(cluster_datapoints.shape[0]):
            sample_cluster_index = cluster_datapoints[sample_idx][1]
            if sample_cluster_index != cluster_index:
                print "ERROR cluster numbers are different: {0} {1}".format(sample_cluster_index, cluster_index)
                continue
            position = cluster_positions[sample_idx]
            x, y = position[1:3]
            #y = self.height - y   # flip y because png uses y as top down, fits uses y from bottom up

            left = x - window_size
            right = x + window_size
            top = y + window_size
            bottom = y - window_size

            colour = self.label_manager.get_color(int(cluster_index))
            #if cluster_index == 1:
            #    colour = [255, 0 ,0]
            #if cluster_index == 2:
            #    colour = [0,0,255]
            #if cluster_index == 3:
            #    colour = [255,100,0]

            # colour sample position
            #img[bottom:top, left:right] = colour
            img[y, x] = colour
            if output_singles:
                #timg[bottom:top, left:right] = colour
                timg[y, x] = colour

            if fits_img != None:
                #fits_img[y,x] = self.label_manager.get_label(int(cluster_index))
                fits_img[y,x] = i + 1

    def create_seg_images(self,
                          positions, datapoint_cluster_index, window_size,
                          save_intermediates = np.array([]), output_singles=False, output_fits=False):

        _img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        _img[:, :] = [255, 255, 255]

        fits_img = None
        if output_fits:
            #fits_img = np.ones((3, self.height, self.width), dtype=np.uint8)
            #fits_img *= 255 # set to white background
            fits_img = np.zeros((self.height, self.width), dtype=np.uint8)  # 0 is background

        self.__colour_samples(_img, fits_img, positions,
                        datapoint_cluster_index, window_size,
                        save_intermediates, output_singles=output_singles)

        img = self.__get_sub_image(_img)
        img.save(self.output_folder_path + 'output_seg_image_' + str(self.test_number) +'_' +
                 str(self._num_clusters) + '.png')

        fits_img_out = None
        if output_fits:
            fits_img_out = get_fits_sub_img(fits_img, self.rect)

        return _img, fits_img_out

    def __get_sub_image(self, img):
        bottom = self.rect[0]
        top = self.rect[1]
        left = self.rect[2]
        right = self.rect[3]
        return Image.fromarray(img[bottom:top, left:right])
        #return Image.fromarray(img[4051:8505, 3405:6550]) # all abell2744
        #return Image.fromarray(img[3380:5847, 3104:5805]) # macs0416


class LabelManager(object):

    def __init__(self, base_path, narrow, wide):

        narrow_path = base_path + '/' + narrow
        wide_path = base_path + '/' + wide

        print "narrow: {0}".format(narrow_path)
        print "wide: {0}".format(wide_path)

        # 'g:/users/alexh/OneDrive/Data/colors125_3colors_nobin.txt'
        self._colors = self.__load_colors(wide_path)
        # "g:/users/alexh/OneDrive/Data/colors125_narrow_3colors_nobin.txt"
        self._dict_colors_narrow = self.__load_narrow_colors(narrow_path)
        self._num_colors = len(self._colors)

    def __load_narrow_colors(self, color_file_path):
        _dict_colors = {}
        _t_colors = np.loadtxt(color_file_path, delimiter=",")
        for i in range(_t_colors.shape[0]):
            #cluster_index = int(_t_colors[i, 1])
            cluster_index = int(_t_colors[i, 2])
            #row = _t_colors[i, :]
            #row = int(_t_colors[i, 3]) # brain
            #row = int(_t_colors[i, 4]) # gmm
            label = int(_t_colors[i,3]) # activation

            color = [int(_t_colors[i,5]),int(_t_colors[i,6]),int(_t_colors[i,7])]

            #_dict_colors[int(cluster_index)] = label
            _dict_colors[int(cluster_index)] = color

        return _dict_colors

    def __load_colors(self, color_file_path):
        _colors = []
        if(os.path.isfile(color_file_path) == False):
            for i in range(5000):
                _colors.append(np.random.rand(3).astype(np.float32))
            np.savetxt(color_file_path, _colors)
            return np.array(_colors)
        else:
            _colors = np.loadtxt(color_file_path)
        return _colors

    def get_label(self, cluster_id):

        if self._dict_colors_narrow.has_key(cluster_id):
            label = self._dict_colors_narrow[cluster_id]
            return label + 1# 0 is background so add one to shift the labels up

        # not recognized to make it 10, should get here
        print "ouch cluster_id: {0}".format(cluster_id)
        return 10

    def get_color(self, label):

        if self._dict_colors_narrow.has_key(label):
            #colour = self._dict_colors_narrow[label][2:5]
            label = self._dict_colors_narrow[label]

            #colors = [[255, 0, 0], [0, 0, 255], [255, 100, 0], [255, 255, 0]]  # red blue orange yellow
            #colour = colors[label]
            colors = [[255, 212, 0], [0, 0, 255], [255, 80, 0], [255,0,0]]  # red blue orange yellow
            colour = colors[label]
            #colour = np.round(colour*255).astype(np.uint8)
            #return colour
            return label

        temp_color_idx = label

        while temp_color_idx >= self._num_colors:
            temp_color_idx = temp_color_idx - self._num_colors
            if temp_color_idx == 0:
                break

        colour = self._colors[temp_color_idx]
        colour = np.round(colour*255).astype(np.uint8)

        return colour


def get_fits_sub_img(img, rect):
    bottom = rect[0]
    top = rect[1]
    left = rect[2]
    right = rect[3]
    return img[bottom:top, left:right]

def create_fits_rgb_cube(folder_path):
    n = np.zeros((3, 1000, 1000), dtype=np.uint8)
    #n[:, 400:600, 400:600] = np.ones((200,200))*[255,0,0]
    n[0, 400:600, 400:600] = np.ones((200,200))*255
    hdu = pyfits.PrimaryHDU(n)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(folder_path + '/test.fits', clobber=True)

def load_fits(fits_path):
        # open long
    img = pyfits.open(fits_path)
    img_data = img[0].data
    return img

def save_fits(img, image_folder_path, new_fits_file_name):
    print "outputting: " + new_fits_file_name
    img.writeto(image_folder_path + new_fits_file_name)

def save_cutout(output_folder_path, fits_img_path, rect):
    img = pyfits.open(fits_img_path)
    img_data = img[0].data
    img_data = get_fits_sub_img(img_data, rect)
    hdu = pyfits.PrimaryHDU(img_data)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(output_folder_path, clobber=True)
    hdulist.close()
    img.close()

def main(config):

    window_size = 0
    num_clusters = 0
    test_num = 129
    #save_intermediates = True
    output_singles = False
    output_fits = False

    base_path = 'c:/Users/alexh/OneDrive/'
    input_folder_path = base_path + "data/output129_23_06_15_agglom_testing/abell2744/exp1/127/macs0416/"

    output_folder_path = input_folder_path + '/active_color/'


     # 'g:/users/alexh/OneDrive/Data/colors125_3colors_nobin.txt'
    wide_colors = 'colors127_test.txt'
    narrow_colors = 'color_activation_rule_cluster_labels_esh.txt'
    #narrow_colors = 'proximity_activation_rule_cluster_labels.txt'
    label_manager = LabelManager(input_folder_path, narrow=narrow_colors, wide=wide_colors)


    dci_file_name = "dci_vq.txt"
    #dci_file_name = "dci_simple_sf.txt"
    pos_file_name=  "gen_positions.csv"

    intermediates = np.array([1, 3, 6, 9, 12, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100, 150])

    # abell 2744
    height = 12300
    width = 10700
    # --- flipped -- rect = [4051, 8505, 3405, 6550]  # bottom:top, left:righht
    rect = [height-8505, height-4051, 3405, 6550]
    #bb_abell2744 = BoundingBox(left=3405, right=6550, top=12300-4051, bottom=12300-8505)
    # macs0416
    #height = 10000
    #width = 10000
    #rect = [3380, 5847, 3104, 5805]  # bottom:top, left:righht
    #rect = [height-5847, height-3380, 3104, 5805]
    #bb_macsj0416 = BoundingBox(left=3104, right=5805, top=10000-3380, bottom=10000-5847)


    print "Loading files"

    positions = np.loadtxt(input_folder_path + pos_file_name, delimiter=",").astype(np.int32)
    datapoint_cluster_index = np.loadtxt(input_folder_path + dci_file_name, delimiter="\t").astype(np.int32)

    print "Finished loading files"

    seg_image = SegImage(output_folder_path, rect, width, height, num_clusters, test_num, label_manager)

    final_img, fits_img = seg_image.create_seg_images(positions, datapoint_cluster_index, window_size,
                                            save_intermediates=intermediates, output_singles=output_singles,
                                            output_fits=output_fits)

    if output_fits:
        fits_img_path_435 = 'c:/Users/alexh/OneDrive/Data/Images/v1.0/macs0416/hlsp_frontier_hst_acs-30mas_macs0416_f435w_v1.0_drz.fits'
        fits_img_path_606 = 'c:/Users/alexh/OneDrive/Data/Images/v1.0/macs0416/hlsp_frontier_hst_acs-30mas_macs0416_f606w_v1.0_drz.fits'
        fits_img_path_814 = 'c:/Users/alexh/OneDrive/Data/Images/v1.0/macs0416/hlsp_frontier_hst_acs-30mas_macs0416_f814w_v1.0_drz.fits'
        #fits_img_path_435 = 'c:/Users/alexh/OneDrive/Data/Images/v1.0/abell2744/hlsp_frontier_hst_acs-30mas_abell2744_f435w_v1.0_drz.fits'
        #fits_img_path_606 = 'c:/Users/alexh/OneDrive/Data/Images/v1.0/abell2744/hlsp_frontier_hst_acs-30mas_abell2744_f606w_v1.0_drz.fits'
        #fits_img_path_814 = 'c:/Users/alexh/OneDrive/Data/Images/v1.0/abell2744/hlsp_frontier_hst_acs-30mas_abell2744_f814w_v1.0_drz.fits'
        bottom = rect[0]
        top = rect[1]
        left = rect[2]
        right = rect[3]
        # save original cutouts
        save_cutout(output_folder_path + '/ab2744_435_not_thresholded.fits', fits_img_path_435, rect)
        save_cutout(output_folder_path + '/ab2744_606_not_thresholded.fits', fits_img_path_606, rect)
        save_cutout(output_folder_path + '/ab2744_814_not_thresholded.fits', fits_img_path_814, rect)

        # save cutouts
        hdu = pyfits.PrimaryHDU(fits_img)
        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto(output_folder_path + '/seg.fits', clobber=True)

    print "Finished"

# #######################################################################################
# # Main
# #######################################################################################

if __name__ == "__main__":
    args = [sys.argv[0], '../../config.ini']
    main(astro_config.get_config(args))
