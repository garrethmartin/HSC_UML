__author__ = 'AlexH'
import sys
import os
import numpy as np
import glob
import re
from astropy.io import fits as pyfits
import config
import log

def get_fits_image_memmap(filename=''):
    img = pyfits.open(filename, memmap=True)
    return img


def get_fits_image_matrix(filename=''):
    img = pyfits.open(filename)
    img_data = img[0].data  # get the image
    return img_data  ## return the memory mapped file


def get_clip(self, image, x, y, window_size):
    top = y + window_size
    bottom = y - window_size
    left = x - window_size
    right = x + window_size

    return image[bottom:top, left:right]


def get_dict_of_seg_images(input_path):
    seg_images = {}
    seg_images_list = glob.glob(input_path + "object_*.png")
    p = re.compile('object_([0-9]+)_([0-9]+).png')
    for i in range(len(seg_images_list)):
        seg_image_file_path = os.path.basename(seg_images_list[i])
        m = p.match(seg_image_file_path)
        obj_id = m.groups()[0]
        seg_images[int(obj_id)] = seg_image_file_path
    return seg_images


def output_catalogue_cutouts(fits_path, rms_path, wht_path, input_path, output_path, header_values=None):

    pymorph_cat = []

    image = get_fits_image_memmap(fits_path)
    rms = get_fits_image_memmap(rms_path)
    #wht = get_fits_image_matrix(wht_path)

    # load catalogue of all objects over 40 patches
    #cat = np.loadtxt(input_path + 'object_catalogue_macs0416.txt', dtype=np.int, delimiter=' ')
    cat = np.loadtxt(input_path + 'object_catalogue.txt', dtype=np.int, delimiter=' ')

    # load classifications for all objects
    #classifications = np.loadtxt(input_path + 'macs0416_aggclu_galaxy_labels.txt', dtype=np.int, delimiter=' ')

    #class_folder_path = output_path + 'gms'

    for i in range(cat.shape[0]):

        galaxy = cat[i,:]

        # objid numpatches width height     cleft cright ctop cbottom   cx cy bleft bright btop bbottom
        obj_id = galaxy[0]

        #obj_type = classifications[classifications[:, 0] == obj_id][0][1]

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

        #obj_type = cat[14]

        size = 149
        diff = 149/2
        # calc
        l = obj_x - diff
        r = obj_x + diff
        if r-l < size:
            r += (size-(r-l))

        t = obj_y + diff
        b = obj_y - diff
        if t-b < size:
            t += (size-(t-b))

        clip = image[0].data[b:t, l:r]
        rms_clip = rms[0].data[b:t, l:r]
        #wht_clip = wht[b:t, l:r]

        #clip = np.flipud(clip)
        # make class folder
        #class_folder_path = output_path + 'class_149_{0}'.format(obj_type)

        if os.path.isdir(output_path) == False:
            os.mkdir(output_path)

        gal_id = "{0:05d}_r_stamp".format(obj_id)
        image_file_name = gal_id + ".fits"
        #weight_file_name = gal_id + "_eight.fits"
        rms_file_name = gal_id + "_W.fits"
        #psf_file_name = "00000_r_psf.fits"

        #output_file_path = class_folder_path + '/object_{0}_{1}_{2}.fits'.format(obj_id, numpatches, obj_type)
        #rms_output_file_path = class_folder_path + '/object_{0}_{1}_{2}_rms.fits'.format(obj_id, numpatches, obj_type)
        #wht_output_file_path = class_folder_path + '/object_{0}_{1}_{2}_wht.fits'.format(obj_id, numpatches, obj_type)

        output_fits(output_path + '/' + image_file_name, clip, header_values)
        #output_fits(class_folder_path + '/' + weight_file_name, rms_clip)
        output_fits(output_path + '/' + rms_file_name, rms_clip)

        cat_row = [gal_id, image_file_name, rms_file_name]
        pymorph_cat.append(cat_row)

        #hdu = pyfits.PrimaryHDU(clip)
        #hdulist = pyfits.HDUList([hdu])
        #hdulist.writeto(output_file_path, clobber=True)
        #hdulist.close()

        # copy seg image
        #source_seg_file_path = input_path + seg_images[obj_id]
        #sh.copyfile(source_seg_file_path, class_folder_path + '/' + seg_images[obj_id])

    np.savetxt(input_path + '/pymorph_cat_r_1.cat', pymorph_cat, fmt='%s')

def output_fits(output_file_path, clip, header_values=None):
    hdu = pyfits.PrimaryHDU(clip)
    hdulist = pyfits.HDUList([hdu])

    if header_values:
        for k, v in header_values.items():
            hdulist[0].header[k] = v

    hdulist.writeto(output_file_path, clobber=True)
    hdulist.close()

def main(config):
    #image_base_path = 'F:/Users/alexh/OneDrive/Data/Images/v1.0/macs0416/'
    image_base_path = '/home/ah14aeb/Downloads/'
    #fits_file_path = image_base_path + '/hst_images/macs0416/hlsp_frontier_hst_acs-30mas_macs0416_f435w_v1.0_drz.fits'
    #rms_file_path = image_base_path + 'hlsp_frontier_hst_acs-30mas_macs0416_f435w_v1.0_rms.fits'
    #wht_file_path = image_base_path + 'hlsp_frontier_hst_acs-30mas_macs0416_f435w_v1.0_wht.fits'

    fits_file_path = image_base_path + '/hst_images/macs1149/hlsp_frontier_hst_acs-30mas_macs1149_f435w_v1.0-epoch2_drz.fits'
    rms_file_path = image_base_path + 'hlsp_frontier_hst_acs-30mas_macs1149_f435w_v1.0-epoch2_rms.fits'
    wht_file_path = image_base_path + 'hlsp_frontier_hst_acs-30mas_macs1149_f435w_v1.0-epoch2_wht.fits'


    #base_path = 'D:/Users/alexh/OneDrive/Data/output127_28_05_15_gen_bestimages_nonzero/abell2744/exp1/macs0416_conn_comps2/output1pixel2/'
    input_base_path = '/home/ah14aeb/Software/pymorph/examples/5sig_nobin_macs1149/gms435/'
    output_base_path = '/home/ah14aeb/Software/pymorph/examples/5sig_nobin_macs1149/gms435/data/'

    # pulled from macs0416 header, setting exptime to 1 because in counts per second
    #header_values = {'EXPTIME': 1, 'NCOMBINE': 104, 'GAIN': 2.0, 'RDNOISE': 4.0} # 814
    header_values = {'EXPTIME': 1, 'NCOMBINE': 44, 'GAIN': 2.0, 'RDNOISE': 4.0}  # 435

    output_catalogue_cutouts(fits_file_path, rms_path=rms_file_path, wht_path=wht_file_path,
                            input_path=input_base_path, output_path=output_base_path, header_values=header_values)


# #######################################################################################
# # Main
# #######################################################################################

logger = None

if __name__ == "__main__":

    #config = config.get_config(sys.argv)
    #log.configure_logging(config['log_file_path'])
    #logger = log.get_logger("montage_149")

    #logger.debug("*** Starting ***")
    main(None)
    #logger.debug("*** Finished ***")