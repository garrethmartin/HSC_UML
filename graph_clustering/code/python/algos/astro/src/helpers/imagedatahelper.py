__author__ = 'ah14aeb'
import os
import numpy as np
import random
import re
from astropy.io import fits as pyfits

class ImageDataHelper(object):

    _num_images = 0
    _image_paths = None
    _image_files = None
    _image_range = None
    _image_shape = None
    _image_means = []
    _gal_clusters = []
    _wavelengths = []
    _x_offset = 0
    _y_offset = 0

    def __init__(self, logger, options, extension=".fits", use_mem_map=False, normalize=False):

        self.logger = logger
        self._image_folder_path = options.image_folder_path

        copy_fits_data = True
        if options.left is None and options.bottom is None:
            copy_fits_data = False
            self._x_offset = 0
            self._y_offset = 0
            self._y_end = 0
            self._x_end = 0

        training_image_paths = []
        image_files = os.listdir(options.image_folder_path)
        for i, t in enumerate(image_files):
            if t.endswith(extension) is False:
                logger.info("Skipping file: {0} as it does not match extension: {1}".format(t, extension))
                continue
            training_image_paths.append(t)

        #training_image_paths.sort(reverse=True)
        training_image_paths.sort()

        image_data = []
        for image_iter in range(len(training_image_paths)):
            training_image_path = options.image_folder_path + '/' + training_image_paths[image_iter]

            img = pyfits.open(training_image_path, mode='readonly', use_mem_map=use_mem_map)
            if copy_fits_data:
                logger.info("copying fits section into ram: {0} {1} {2} {3}".format(
                    options.bottom, options.top, options.left, options.right))
                pic = np.array(img[0].data[options.bottom:options.top, options.left:options.right],
                               copy=True)  # get the image
                img.close()
                del img
                # save for adjusted access
                self._x_offset = options.left
                self._y_offset = options.bottom
                self._x_end = options.right
                self._y_end = options.top
                image_data.append(pic)
            else:
                pic = img[0].data
                image_data.append(pic)

            if self._image_shape is None:
                self._image_shape = pic.shape
            if pic.shape != self._image_shape:
                logger.warning("Error fits are different sizes: {0} {1} {2}".format(
                    self._image_shape, pic.shape, training_image_path))

            logger.info("Index: {0} Image Name: {1}".format(image_iter, training_image_paths[image_iter]))

        for i in range(len(training_image_paths)):
            m = re.match("hlsp_candels_hst_(acs|wfc3)_([a-z]+)-tot_(f[0-9]+w)_", training_image_paths[i])
            #hlsp_candels_hst_acs_gn-tot-60mas_f606w_v1.0_drz_thresholded_3sigma.fits
            self._gal_clusters.append(m.groups(0)[1])
            self._wavelengths.append((m.groups(0)[2]))
            logger.info("m.groups(0)[1]: {0} [2] {1}".format(m.groups(0)[1], m.groups(0)[2]))

        self._image_paths = np.array(training_image_paths)
        self._image_files = image_data  # don't add to numpy as it will load into RAM leave as memory mapped files.
        self._num_images = len(self._image_paths)
        self._image_range = range(self._num_images)


    @staticmethod
    def __get_fits_image_matrix(filename=''):
        img = pyfits.open(filename)
        img_data = img[0].data  # get the image
        return img_data  ## return the memory mapped file

    def get_wavelengths(self):
        return np.array(self._wavelengths)

    def get_image(self, image_idx):
        return self._image_files[image_idx]

    def get_image_count(self):
        return self._num_images

    def get_image_shape(self):
        return self._image_shape

    def get_image_mean(self, image_index):
        return self._image_means[image_index]

    def get_adjusted_image_data(self, image_idx, xx, yy):
        image_data = self._image_files[image_idx]
        return image_data[yy - self._y_offset, xx - self._x_offset]

    def get_adjusted_patch(self, position, window_size):
        image_index = position[0]
        x = position[1]
        y = position[2]
        x -= self._x_offset
        y -= self._y_offset
        #print "x: {0} y:{1}".format(x, y)
        return self.__get_clip(image_index, x, y, window_size)


    def get_patch(self, position, window_size):
        image_index = position[0]
        x = position[1]
        y = position[2]
        #print "x: {0} y:{1}".format(x, y)
        return self.__get_clip(image_index, x, y, window_size)

    def get_pixel(self, position):
        image_index = position[0]
        x = position[1]
        y = position[2]
        image = self._image_files[image_index]
        return image[y, x]

    def get_rectangle(self, image_index, left, right, top, bottom):
        """
        :type image_index: int
        :param left:
        :param right:
        :param top:
        :param bottom:
        :return:
        """
        image = self._image_files[image_index]
        return image[bottom:top, left:right]

    def __is_zero(self, x, y):
        is_zero = False
        for i in range(self._num_images):
            if self._image_files[i][y, x] == 0:
                is_zero = True
                break
        return is_zero

    def __are_all_zero(self, x, y):
        is_zero = True
        for i in range(self._num_images):
            if self._image_files[i][y, x] > 0:
                is_zero = False
                break
        return is_zero

    def __get_clip(self, image_index, x, y, window_size):

        image = self._image_files[image_index]

        top = y + window_size
        bottom = y - window_size
        left = x - window_size
        right = x + window_size

        return image[bottom:top, left:right]

    @staticmethod
    def set_patch_rect(image, position, window_size, color):
        image_index = position[0]
        x = position[1]
        y = position[2]

        top = y + window_size
        bottom = y - window_size
        left = x - window_size
        right = x + window_size

        image[bottom:top, left:right] = color

    def get_patch_all_images_from_pos(self, position, window_size):
        return self.get_patch_all_images(position[1], position[2], window_size)

    def get_patch_all_images_with_check(self, xpos, ypos, window_size, all_zero=True):

        if all_zero == True and self.__is_zero(xpos, ypos) == True:
            return None, None, None

        if all_zero == False and self.__are_all_zero(xpos, ypos) == True:
            return None, None, None

        return self.get_patch_all_images(xpos, ypos, window_size)

    def get_adjusted_patch_all_images_with_check(self, xpos, ypos, window_size, all_zero=True):

        offset_xpos = xpos - self._x_offset
        offset_ypos = ypos - self._y_offset

        if all_zero == True and self.__is_zero(offset_xpos, offset_ypos) == True:
            return None, None, None

        if all_zero == False and self.__are_all_zero(offset_xpos, offset_ypos) == True:
            return None, None, None

        patches = []
        positions = []
        filters = []
        for i in range(self._num_images):
            position = np.array([0, 0, 0])
            position[0] = i
            position[1] = xpos
            position[2] = ypos
            r_clip = self.__get_clip(i, offset_xpos, offset_ypos, window_size)
            patches.append(r_clip)
            positions.append(position)
            filters.append(self._wavelengths[i])

        return patches, positions, filters

    def get_patch_all_images(self, xpos, ypos, window_size):
        patches = []
        positions = []
        filters = []
        for i in range(self._num_images):
            position = np.array([0, 0, 0])
            position[0] = i
            position[1] = xpos
            position[2] = ypos
            r_clip = self.get_patch(position, window_size)
            patches.append(r_clip)
            positions.append(position)
            filters.append(self._wavelengths[i])
        return patches, positions, filters

    def get_random_patch_all_images(self, bounding_box, window_size, non_zero=False):
        # get random position
        xpos, ypos = bounding_box.get_random_position()

        count = 0
        if non_zero == True:
            while (self.__is_zero(xpos, ypos) == True):   #__are_all_zero
            #while (self.__are_all_zero(xpos, ypos) == True):
                xpos, ypos = bounding_box.get_random_position()
                count +=1

        if count > 2000:
            self.logger.info("random point non zero count: {0}".format(count))

        patches = []
        positions = []
        filters = []

        for i in range(self._num_images):
            position = np.array([0, 0, 0])
            position[0] = i # image index
            position[1] = xpos
            position[2] = ypos

            r_clip = self.get_patch(position, window_size)
            if r_clip is None:
                self.logger.error("ERROR*********")

            patches.append(r_clip)
            positions.append(position)
            filters.append(self._wavelengths[i])

        return patches, positions, filters

    def get_random_patch(self, bounding_box, window_size, zero_pixel_limit=-1):

        use_threshold = False
        if zero_pixel_limit > -1:
            use_threshold = True

        position = np.array([0, 0, 0])

        r_clip = None
        i = 0
        while i < 1000:

            i += 1

            position[0] = random.choice(self._image_range)  # random image
            position[1] = random.choice(bounding_box.xpixel_range)  # random x pos in bounding box
            position[2] = random.choice(bounding_box.ypixel_range)  # random y pos in bounding box

            r_clip = self.get_patch(position, window_size)

            if use_threshold:
                zero_pixes = r_clip[r_clip <= 0].shape[0]
                if zero_pixes > zero_pixel_limit:
                    #  print "zero_pixes: {0} limit: {1}".format(zero_pixes, _zero_pixel_limit)
                    continue

            break

        if r_clip is None:
            self.logger.error("ERROR*********")

        return r_clip, position
