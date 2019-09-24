__author__ = 'alex'
import os
import sys
import numpy as np
import config
import log
from astropy.io import fits as pyfits
from astropy.stats import sigma_clipped_stats
from scipy.ndimage import rotate

import matplotlib.pyplot as plt


# http://photutils.readthedocs.org/en/latest/photutils/background.html

def get_background_stats(background_clip, display_background=False):
    """ can use ds9 to do the same. Draw a line and see the variation along it """
    background_mean = np.mean(background_clip)
    background_std = np.std(background_clip)
    background_rms = np.sqrt(np.mean(np.square(background_clip)))
    logger.info("background mean: {0}".format(background_mean))
    if display_background:
        plt.imshow(background_clip)
        plt.show()
    return background_mean, background_rms, background_std

def get_mask(image_data, mask_height, mask_width, mask_rotation, show_mask=False):
    """mask contains True for 'bad' pixels and False for good"""

    hst_height, hst_width = image_data.shape

    mask = np.ones((mask_height, mask_width))
    mask2 = rotate(mask, mask_rotation) ## -24.
    height, width = mask2.shape
    offset_x = (hst_width - width) / 2.
    offset_y = (hst_height - height) / 2.
    mask3 = np.zeros((hst_height, hst_width))
    mask3[offset_y:offset_y+height, offset_x:offset_x+width] = mask2

    background_mask = (mask3 == False)
    if show_mask:
        plt.imshow(background_mask)
        plt.show()

    return background_mask, mask3


def main(config):

    image_folder_path = config['thresholding']['image_folder_path']
    sigma_clip = float(config['thresholding']['clip_sigma'])
    sigma_multiplier = float(config['thresholding']['sigma_multiplier'])
    sigma_iters = int(config['thresholding']['sigma_iterations'])
    mask_x = int(config['thresholding']['mask_x'])
    mask_y = int(config['thresholding']['mask_y'])
    mask_width = int(config['thresholding']['mask_width'])
    mask_height = int(config['thresholding']['mask_height'])
    mask_rotation = 0.0 #float(config['thresholding']['mask_rotation'])

    logger.info("image folder: {0}".format(image_folder_path))
    logger.info("sigma clip: {0} sigma multiplier: {1}".format(sigma_clip, sigma_multiplier))
    logger.info("mask_height: {0}  mask_width: {1} mask_x: {2} mask_y: {3} mask_rotation: {4}".format(mask_height,
                                                            mask_width, mask_x, mask_y, mask_rotation))
    logger.info("sigma_iterations: {0}".format(sigma_iters))

    image_files = os.listdir(image_folder_path)

    for image_idx in range(len(image_files)):

        #if not "814" in image_files[image_idx]:
        #    print("skipping as not 814 {0}".format(image_files[image_idx]))
        #    continue
        image_file_name = image_files[image_idx]
        short_file_name, file_ext = os.path.splitext(image_file_name)
        if not '_gs-tot' in short_file_name:
            logger.info("skipping: {0}".format(image_file_name))
            continue
        if 'thresholded' in short_file_name or not short_file_name.endswith('drz') or file_ext != '.fits':
            logger.info("skipping: {0}".format(image_file_name))
            continue

        logger.info("Thresholding: {0}".format(image_file_name))

        image_file_path = image_folder_path + image_file_name

        img = pyfits.open(image_file_path)
        img_data = img[0].data[mask_y:mask_y+mask_height, mask_x:mask_x + mask_width]

        # background_clip = img_data[5845:5920, 7300:7350]
        # background_mean, background_rms, background_std = get_backround_stats(background_clip)

        # run sigma clip to estimate background level
        #mask = img_data == 0.   # mask away the 0 pixels that have no signal
        #background_mask, mask = get_mask(img_data, mask_height, mask_width, mask_rotation, show_mask=False)
        #logger.info("Got mask")
        #clipped_mean, clipped_median, clipped_std = sigma_clipped_stats(img_data, sigma=sigma_clip, iters=7,
        #                                                                mask=background_mask)
        clipped_mean, clipped_median, clipped_std = sigma_clipped_stats(img_data, sigma=sigma_clip, iters=sigma_iters)

        # calc threshold by multiplying the estimated background (clipped_std) by the input variable multiplier (5?)
        threshold = sigma_multiplier * clipped_std

        logger.info("Clipped values: mean: {0} median: {1} std: {2}".format(clipped_mean, clipped_median, clipped_std))
        logger.info("multiplier: {0}  threshold: {1}".format(sigma_multiplier, threshold))

        # threshold the image -- set all values below sky estimation to 0.
        #img_data[img_data < threshold] = 0.
        img[0].data[img[0].data < threshold] = 0.

        # save as new image
        #img[0].data = img_data  # replace the existing data with the thresholded data
        new_fits_file_name = short_file_name + '_thresholded_{0}sigma'.format(int(sigma_multiplier)) + file_ext
        logger.info("saving: " + new_fits_file_name)
        img.writeto(image_folder_path + new_fits_file_name, clobber=True)

        # save mask
        #img[0].data = mask # replace the existing data with the thresholded data
        #new_fits_file_name = short_file_name + '_mask' + file_ext
        #logger.info("saving: " + new_fits_file_name)
        #img.writeto(image_folder_path + new_fits_file_name, clobber=True)

        img.close()

        logger.info("Finished thresholding {0}".format(image_file_name))


########################################################################################
# Main
########################################################################################

logger = None

if __name__ == "__main__":

    config = config.get_config(sys.argv)
    log.configure_logging(config['log_file_path'])
    logger = log.get_logger("thresholding")

    logger.debug("*** Starting ***")
    main(config)
    logger.debug("*** Finished ***")
