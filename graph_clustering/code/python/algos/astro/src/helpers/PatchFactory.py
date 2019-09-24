__author__ = 'AlexH'
import numpy as np


class PatchFactory(object):

    def __init__(self, logger, image_data_helper, feature_factory):
        self.image_data_helper = image_data_helper
        self.logger = logger
        self.feature_factory = feature_factory

    def get_features_all_pixels(self, options, bounding_box, image_files):
        width = bounding_box.width
        height = bounding_box.height
        stride = options.stride

        self.logger.info("Extracting up to {0} samples from image size w: {1} h: {2} stride: {3}".format(
            (width/stride)*(height/stride), width, height, stride))

        samples, positions = self.get_all_samples(options=options, bounding_box=bounding_box, image_files=image_files)

        self.logger.info("samples shape: {0}  positions shape: {1}".format(samples.shape, positions.shape))

        return samples, positions

    def get_all_samples(self, options, bounding_box, image_files):

        samples = []
        positions = []
        window = options.window_size
        image_size = [window*2, window*2]
        #num_images = self.image_data_helper._num_images
        num_pixels = image_size[0]*image_size[1]

        counter = 0
        zero_counter = 0

        for x in bounding_box.x_pixel_range:
            for y in bounding_box.y_pixel_range:

                patches = self.image_data_helper.get_adjusted_patch_all_images(x, y, window)
                if not self.check_patches(patches, image_files, num_pixels, window):
                    counter += 1
                    zero_counter += 1
                    continue

                # threshold patches by setting all pixels below threshold to zero.
                patches = self.threshold_patches(patches, image_files)

                sample, num_ps_values = self.feature_factory.process_patches(patches)

                samples.append(sample.tolist())
                positions.append(np.array([0, x, y]))

                if counter % 10000 == 0:
                    self.logger.info("processed pixels:{0} non_zero_patches: {1} x: {2} y: {3}".format(
                        counter, counter-zero_counter, x, y))
                counter += 1

        return np.array(samples), np.array(positions)

    def threshold_patches(self, patches, image_files):
        for patch_iter in range(len(patches)):
            wavelength = self.image_data_helper._wavelengths[patch_iter]
            threshold = image_files[wavelength].threshold
            patch = patches[patch_iter]
            patch[patch < threshold] = 0
            patches[patch_iter] = patch
        return patches

    def check_patches(self, patches, image_files, num_pixels, window):

        skip = True

        for patch_iter in range(len(patches)):
            wavelength = self.image_data_helper._wavelengths[patch_iter]
            threshold = image_files[wavelength].threshold

            if patches[patch_iter][window, window] > threshold: # check if at least one wavelength above threshold
                skip = False

            # check if one or more of the wavelengths lack coverage
            # set to 0.8 in case some pixels are 0 - should be much fewer than 20%
            if np.count_nonzero(patches[patch_iter]) < (num_pixels*0.8):
                skip = True
                break

        if skip == True:
            return False # not ok
        else:
            return True # ok
