__author__ = 'ah14aeb'
import os
import numpy as np
import random
import re
from astropy.io import fits as pyfits

class FitsHelper(object):

    def __init__(self, logger, image_folder_path, image_files_dict, required_wavelengths, rect=None, use_mem_map=False):

        self.logger = logger

        self._wavelengths = []
        self._image_shape = None
        self._num_images = 0
        self._image_paths = []
        self._image_files = []

        copy_fits_data = True
        if rect is None:
            copy_fits_data = False
            self._x_offset = 0
            self._y_offset = 0
            self._y_end = 0
            self._x_end = 0
        else:
            # save for adjusted access
            self._x_offset = rect.left
            self._y_offset = rect.bottom
            self._x_end = rect.right
            self._y_end = rect.top

        image_data = []
        for wavelength in required_wavelengths:
        #for wavelength, image_file_details in image_files_dict.iteritems():
            image_file_details = image_files_dict[wavelength]

            fits_image_file_name = image_file_details.file_name
            logger.info("loading fitshelper wavelength: {0} Image Name: {1}".format(
                wavelength, fits_image_file_name))

            self._wavelengths.append(wavelength)
            self._image_paths.append(fits_image_file_name)

            img = pyfits.open(image_folder_path + fits_image_file_name, mode='readonly', use_mem_map=use_mem_map)
            # For HSC, the data is in img[1]
            if img[0].data == None:
                hdu_image_loc = 1
            else:
                hdu_image_loc = 0
            if copy_fits_data:
                logger.info("copying fits section into ram: {0} {1} {2} {3}".format(
                    rect.bottom, rect.top, rect.left, rect.right))
                pic = np.array(img[hdu_image_loc].data[rect.bottom:rect.top, rect.left:rect.right],
                               copy=True, order='C')
                #pic = np.array(img[0].data[rect.bottom:rect.top, rect.left:rect.right], copy=True, order='C')
                img.close()
                del img
                image_data.append(pic)
            else:
                pic = img[hdu_image_loc].data
                #pic = img[0].data
                image_data.append(pic)

            if self._image_shape is None:
                self._image_shape = pic.shape
            else:
                if self._image_shape[0] != pic.shape[0]:
                    logger.error("image file is different shape: {0} {1} {2}".format(
                        self._image_shape, pic.shape, fits_image_file_name))
                if self._image_shape[1] != pic.shape[1]:
                    logger.error("image file is different shape: {0} {1} {2}".format(
                        self._image_shape, pic.shape, fits_image_file_name))

            logger.info("finished loading fitshelper wavelength: {0} Image Name: {1}".format(
                wavelength, fits_image_file_name))

        self._image_files = image_data
        self._num_images = len(self._image_paths)
        self._image_range = range(self._num_images)

    def close(self):
        while len(self._image_files) > 0:
            del self._image_files[0]

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

    def get_adjusted_rect(self, image_index, bottom, top, left, right):
        left -= self._x_offset
        right -= self._x_offset
        top -= self._y_offset
        bottom -= self._y_offset
        return self.get_rectangle(image_index, bottom, top, left, right)

    def get_image_index(self, in_wavelength):
        i = 0
        for wavelength in self._wavelengths:
            if in_wavelength == wavelength:
                return i
            i += 1
        return -1

    def set_background_level(self, image_index, sigma):
        self._sigmas[self._wavelengths[image_index]] = sigma

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

    def get_wavelength_rectangle(self, wavelength, bottom, top, left, right):
        """
        :type wavelength: string
        :param bottom:
        :param top:
        :param left:
        :param right:
        :return: numpy.array([])
        """
        image_index = self.get_image_index(wavelength)
        return self.get_adjusted_rect(image_index, bottom, top, left, right)

    def get_rectangle(self, image_index, bottom, top, left, right):
        """
        :type image_index: int
        :param bottom:
        :param top:
        :param left:
        :param right:
        :return:
        """
        image = self._image_files[image_index]
        return image[bottom:top, left:right]

    def __all_below_sigma(self, x, y):
        is_below_sigma = True
        for i in range(self._num_images):
            if self._image_files[i][y, x] > self._sigmas[i]:
                is_below_sigma = False
                break
        return is_below_sigma

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

    def get_adjusted_patch_all_images(self, x_pos, y_pos, window_size):

        offset_xpos = x_pos - self._x_offset
        offset_ypos = y_pos - self._y_offset

        patches = []
        for i in range(self._num_images):
            r_clip = self.__get_clip(i, offset_xpos, offset_ypos, window_size)
            patches.append(r_clip)

        return patches

    def get_adjusted_patch_all_images_with_check(self, xpos, ypos, window_size, ret_none_when_all_below_sigma=True):

        offset_xpos = xpos - self._x_offset
        offset_ypos = ypos - self._y_offset

        if ret_none_when_all_below_sigma == True and self.__all_below_sigma(offset_xpos, offset_ypos) == True:
            return None, None, None

        patches = []
        positions = []
        #filters = []
        for i in range(self._num_images):
            position = np.array([0, 0, 0])
            position[0] = i
            position[1] = xpos
            position[2] = ypos
            r_clip = self.__get_clip(i, offset_xpos, offset_ypos, window_size)
            patches.append(r_clip)
            positions.append(position)
            #filters.append(self._wavelengths[i])

        return patches, positions #, filters

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
