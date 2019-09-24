__author__ = 'ah14aeb'
import sys
import numpy as np
import config
import log
from helpers.imagedatahelper import ImageDataHelper
import os
import re


class FeatureOptions(object):

    def __init__(self, config):
        self.output_folder_path = config['output_folder_path']
        self.image_folder_path = config['image_folder_path']
        self.positions_path = config['positions_path']
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None

    def print_options(self):
        logger.info("image_folder_path: {0}".format(self.image_folder_path))
        logger.info("positions path: {0}".format(self.positions_path))
        logger.info("left: {0} right: {1} bottom: {2} top: {3}".format(self.left, self.right, self.bottom, self.top))

def process_positions(config):
    options = FeatureOptions(config)
    options.print_options()
    idh = ImageDataHelper(logger, options, extension="drz.fits")
    position_files = [f for f in os.listdir(options.positions_path) if re.match(r'(model|gen)_positions_[0-9]+.csv', f)]
    for position_file in position_files:
        logger.info("Processing position file: {0}".format(position_file))
        m = re.match('(model|gen)_positions_([0-9]+).csv', position_file)
        prefix = m.group(1)
        file_num = m.group(2)
        positions = np.loadtxt(options.positions_path + position_file, delimiter=",").astype(np.int)
        process_position_file(logger, config, idh, positions, file_num, prefix)


def process_position_file(logger, config, idh, positions, file_num, prefix):

    output_folder_path = config['output_folder_path']
    sigma_multipliers = config['sigma_multipliers']

    xv = positions[:, 1]  # x
    yv = positions[:, 2]  # y

    for sigma_multiplier in sigma_multipliers:
        sigma_multiplier = float(sigma_multiplier)

        masks = []
        for i in range(idh._num_images):
            sigma = config['sigmas'][idh._wavelengths[i]]
            threshold = float(sigma) * sigma_multiplier

            #image_data = idh.get_image(i)
            values = idh.get_adjusted_image_data(i, xv, yv)
            #values = image_data[yv, xv]

            mask = (values > threshold) * 1
            masks.append(mask)

            logger.info("image: {0} wavelength: {1} sigma: {2} sigma_multiplier: {3} threshold: {4}".format(
                idh._image_paths[i], idh._wavelengths[i], sigma, sigma_multiplier, threshold))

            if idh._wavelengths[i] not in idh._image_paths[i]:
                print("Huge error, wave length not in image file name: {0}".format(idh._image_paths[i]))

        masks = np.array(masks)

        # logical or to combine into one. if a pixel is greater than the threshold on any of the files then it
        # it will be allowed
        final_mask = np.logical_or(masks[0], masks[1])
        if idh._num_images > 2:
            final_mask = np.logical_or(final_mask, masks[2])

        output_file_path = output_folder_path + "/{0}_sigma{1}_positions_maskb_{2}.txt".format(
            prefix, int(sigma_multiplier), file_num)
        np.savetxt(output_file_path, final_mask, delimiter=",", fmt="%i")

        logger.info("Writing file: {0}".format(output_file_path))


def main(config):
    process_positions(config)

def main2(config):

    logger.info(__file__)

    output_folder_path = config['output_folder_path']
    image_folder_path = config['image_folder_path']
    sigmas = config['sigmas']
    sigma_multipliers = config['sigma_multipliers']
    positions_path = config['positions_path']

    logger.info("positions path " + positions_path)

    # load gen_positions
    gen_positions = np.loadtxt(positions_path, delimiter=",").astype(np.int)

    idh = ImageDataHelper(logger, image_folder_path, extension="drz.fits")

    xv = gen_positions[:, 1]  # x
    yv = gen_positions[:, 2]  # y

    for sigma_multiplier in sigma_multipliers:
        sigma_multiplier = float(sigma_multiplier)

        masks = []
        for i in range(idh._num_images):
            sigma = config['sigmas'][idh._wavelengths[i]]
            threshold = float(sigma) * sigma_multiplier

            image_data = idh.get_image(i)
            values = image_data[yv, xv]

            mask = (values > threshold) * 1
            masks.append(mask)

            logger.info("image: {0} wavelength: {1} sigma: {2} sigma_multiplier: {3} treshold: {4}".format(
                idh._image_paths[i], idh._wavelengths[i], sigma, sigma_multiplier, threshold))

            if idh._wavelengths[i] not in idh._image_paths[i]:
                print("Huge error, wave length not in image file name: {0}".format(idh._image_paths[i]))


        masks = np.array(masks)

        # logical or to combine into one. if a pixel is greater than the threshold on any of the files then it
        # it will be allowed
        final_mask = np.logical_or(masks[0], masks[1])
        final_mask = np.logical_or(final_mask, masks[2])

        np.savetxt(output_folder_path + "/sigma{0}_positions_mask.txt".format(
            int(sigma_multiplier)), final_mask, delimiter=",", fmt="%i")



# #######################################################################################
# # Main
# #######################################################################################

logger = None

if __name__ == "__main__":

    config = config.get_config(sys.argv)
    log.configure_logging(config['log_file_path'])
    logger = log.get_logger("object_detection_masks")
    logger.debug("*** Starting ***")
    main(config)
    logger.debug("*** Finished ***")

