import sys
import numpy
import config as cf
import log
import os
import inspect
import pandas as pd
import h5py
from time import gmtime, strftime
from helpers import boundingbox
from helpers import fitshelper
from astropy.stats import sigma_clipped_stats
from helpers.image_types import SkyArea, ImageFile, FieldRect, SigmaRect
from helpers.PatchFactory import PatchFactory
from features.PowerSpectrumFeature import PowerSpectrumFeature


def create_mask_files(options, output_folder_path, fh, image_files, positions, file_num, prefix):

    sigma_multipliers = options.sigma_multipliers

    xv = positions[:, 1]  # x
    yv = positions[:, 2]  # y

    for sigma_multiplier in sigma_multipliers:
        sigma_multiplier = float(sigma_multiplier)

        masks = []
        for i in range(fh._num_images):
            wavelength = fh._wavelengths[i]
            sigma = image_files[wavelength].sigma
            threshold = float(sigma) * sigma_multiplier

            values = fh.get_adjusted_image_data(i, xv, yv)

            mask = (values > threshold) * 1
            masks.append(mask)

            logger.info("image: {0} wavelength: {1} sigma: {2} sigma_multiplier: {3} threshold: {4}".format(
                fh._image_paths[i], fh._wavelengths[i], sigma, sigma_multiplier, threshold))

            if fh._wavelengths[i] not in fh._image_paths[i]:
                print("Huge error, wave length not in image file name: {0}".format(fh._image_paths[i]))

        masks = numpy.array(masks)

        # logical or to combine into one. if a pixel is greater than the threshold on any of the files then it
        # it will be allowed
        final_mask = numpy.logical_or(masks[0], masks[1])
        if fh._num_images > 2:
            final_mask = numpy.logical_or(final_mask, masks[2])

        output_file_path = output_folder_path + "/{0}_sigma{1}_positions_mask_{2}.txt".format(
            prefix, int(sigma_multiplier), file_num)
        numpy.savetxt(output_file_path, final_mask, delimiter=",", fmt="%i")

        logger.info("Writing file: {0}".format(output_file_path))


def calc_rectangle(image_shape, size_pc):

    centre_x = image_shape[0] / 2
    centre_y = image_shape[1] / 2

    # try 20% of width or max 1000 pixels
    width = max(image_shape[0] * size_pc, 250)
    height = max(image_shape[1] * size_pc, 250)

    if width > image_shape[0]:
        width = image_shape[0]

    if height > image_shape[1]:
        height = image_shape[1]

    l = centre_x - width/2
    r = centre_x + width/2
    b = centre_y - height/2
    t = centre_y + height/2

    return int(b), int(t), int(l), int(r)


def guess_sigma_region(wavelength, fh):
    # get the size of the first image
    image_index = fh.get_image_index(wavelength)
    image_shape = fh.get_image_shape()

    #b = 0
    #l = 0
    #t = image_shape[0] - 1
    #r = image_shape[1] - 1
    #return b, t, l, r

    factor = 0.2
    b, t, l, r = calc_rectangle(image_shape, factor)

    # check percentage of isnans and zeros
    c = 0
    i = 0
    while i < 10:

        num_pixels = (t - b) * (r - l)
        sub_image_rect = fh.get_rectangle(image_index, b, t, l, r)
        c = numpy.count_nonzero(sub_image_rect)
        if c > (0.4 * num_pixels):
            break

        # widen
        factor += 0.1
        b, t, l, r = calc_rectangle(image_shape, factor)

        logger.info("iterating sigma regon guess: num pix {0} factor {1} num nonzero {2}".format(num_pixels, factor, c))

        i += 1

    if i == 10:
        logger.info("Warning: iter reached 10 but still no rect so using whole image: {0}".format(i))
        b = 0
        l = 0
        t = image_shape[0] - 1
        r = image_shape[1] - 1
    #return b, t, l, r

    return b, t, l, r


def calc_background_sigma_levels(options, sky_area, wavelength_image_files, fh):

    #, sigma_clip=5, iterations=20
    sigma_clip = int(options.sigma_clip)
    sigma_iterations = int(options.sigma_clip_iterations)

    # the types used to store the sky areas
    #ImageFile = namedtuple("ImageFile", ["id", "wavelength", "sigma_patch", "sigma", "file_path"])
    #SigmaPatch = namedtuple("SigmaPath", ["bottom", "top", "left", "right"])

    for wavelength, image_file in wavelength_image_files.items():

        rect = numpy.array([])
        if sky_area.sigma_rect is not None:
            b = sky_area.sigma_rect.bottom
            t = sky_area.sigma_rect.top
            l = sky_area.sigma_rect.left
            r = sky_area.sigma_rect.right
            rect = fh.get_wavelength_rectangle(wavelength, b, t, l, r)
        else:
            # guess location
            b, t, l, r = guess_sigma_region(wavelength, fh)
            rect = fh.get_wavelength_rectangle(wavelength, b, t, l, r)

        logger.info("Calculating background level for: {0} {1}".format(wavelength, image_file.file_name))

        clipped_mean, clipped_median, clipped_std = sigma_clipped_stats(
            rect, mask_value=0., sigma=sigma_clip, iters=50)

        image_file.sigma = clipped_std
        image_file.threshold = options.min_sigma_multiplier * clipped_std

        # calc threshold by multiplying the estimated background (clipped_std) by the input variable multiplier (5?)
        logger.info("Clipped values wavelength: {0} mean: {1} median: {2} std-sigma: {3} thresh: {4} file: {5}".format(
            image_file.wavelength, clipped_mean, clipped_median,
            clipped_std, image_file.threshold, image_file.file_name))


def remove_already_processed_sky_areas(root_folder, sky_areas, completed_file_name):

    processed_sky_areas = []
    dict_completed = dict()

    if not os.path.isfile(root_folder + completed_file_name):
        return sky_areas, processed_sky_areas

    completed_sky_areas = numpy.loadtxt(root_folder + completed_file_name, delimiter=",")

    if len(completed_sky_areas.shape) == 0:
        completed_sky_area_id = int(completed_sky_areas)
        dict_completed[completed_sky_area_id] = completed_sky_area_id
    else:
        for i in range(completed_sky_areas.shape[0]):
            completed_sky_area_id = completed_sky_areas[i]
            dict_completed[completed_sky_area_id] = completed_sky_area_id

    for sky_area_id, sky_area in sky_areas.items():
        if sky_area_id in dict_completed:
            processed_sky_areas.append(sky_area_id)

    # don't delete during dictionary iteration, so delete after we have copied all the invalid ids
    for processed_sky_area_id in processed_sky_areas:
        if processed_sky_area_id in sky_areas:
            del sky_areas[processed_sky_area_id]
        else:
            logger.info("processed sky area does not exist: {0}".format(processed_sky_area_id))

    logger.info("already_processed sky areas: {0}".format(len(processed_sky_areas)))

    return processed_sky_areas

def validate_sky_area_wavelengths(root_folder, image_folder, sky_areas, wavelengths, errors_file_name):
    # validate
    invalid_sky_areas = []
    for sky_area_id, sky_area in sky_areas.items():
        if len(sky_area.image_files) < len(wavelengths):
            logger.info("removing due to missing wavelengths: {0} {1}".format(sky_area_id, len(sky_area.image_files)))
            invalid_sky_areas.append(sky_area_id)
            continue

        # check if image files exist
        for wavelength, image_file in sky_area.image_files.items():
            if not os.path.isfile(image_folder + image_file.file_name):
                logger.info("file does not exist. sky area: {0} wavelength {1} filename {2}".format(
                    sky_area_id, wavelength, image_folder + image_file.file_name))
                invalid_sky_areas.append(sky_area_id)

    # remove invalid sky areas
    for i in range(len(invalid_sky_areas)):
        if invalid_sky_areas[i] in sky_areas:
            del sky_areas[invalid_sky_areas[i]]

    # output the errors to file
    numpy.array(invalid_sky_areas).tofile(root_folder + errors_file_name, sep=",", format="%s")

    return invalid_sky_areas

def load_sky_areas(root_folder, sky_areas_file_name, image_file_name, wavelengths):

    sky_areas = dict()

    # the types used to store the sky areas
    #SkyArea = namedtuple("SkyArea", ["id", "image_files", "field_rect", "sigma_rect"])
    #ImageFile = namedtuple("ImageFile", ["id", "wavelength", "sigma", "file_name"])
    #SigmaRect = namedtuple("SigmaRect", ["bottom", "top", "left", "right"])
    #FieldRect = namedtuple("FieldRect",["bottom", "top", "left", "right"])

    # id, field, field_rect, sigma_patch
    sky_areas_input = pd.read_csv(root_folder + sky_areas_file_name, sep=',')
    for row_idx in range(sky_areas_input.shape[0]):

        sky_area_id = sky_areas_input.id[row_idx]

        sigma_rect = sky_areas_input.sigma_rect[row_idx]

        #sigma_rect = sky_areas_input.sigma_rect[row_idx].strip()

        if sigma_rect != 'None':
            bits = sigma_rect.strip().split('-')
            sigma_rect = SigmaRect(bottom=int(bits[0]), top=int(bits[1]), left=int(bits[2]), right=int(bits[3]))
        else:
            sigma_rect = None

        field_rect = sky_areas_input.field_rect[row_idx].strip()
        if field_rect != 'None':
            bits = field_rect.strip().split('-')
            field_rect = FieldRect(bottom=int(bits[0]), top=int(bits[1]), left=int(bits[2]), right=int(bits[3]))
        else:
            field_rect = None

        sky_area = SkyArea(id=sky_area_id, image_files={}, field_rect=field_rect, sigma_rect=sigma_rect)
        sky_areas[sky_area_id] = sky_area


    # id, field, wavelength, sigma_patch, file_path
    gen_images = pd.read_csv(root_folder + image_file_name, sep=',')

    for row_idx in range(gen_images.shape[0]):

        id = gen_images.id[row_idx]
        sky_area_id = gen_images.sky_area_id[row_idx]
        wavelength = str(gen_images.wavelength[row_idx])
        wavelength = wavelength.strip()
        file_name = gen_images.file_name[row_idx].strip()

        if wavelength not in wavelengths:
            logger.info("wavelength doesn't exist: {0} {1} {2}".format(wavelength, sky_area_id, file_name))
            continue

        im = ImageFile(id=id, wavelength=wavelength, sigma=None, file_name=file_name)

        if sky_area_id not in sky_areas:
            logger.error("Error sky area from general not in sky areas: {0} {1} {2}".format(sky_area_id, wavelength,
                                                                                            file_name))
            sky_areas[sky_area_id] = SkyArea(sky_area_id, {}, None, None)

        sky_area = sky_areas[sky_area_id]
        if wavelength not in sky_area.image_files:
            sky_area.image_files[wavelength] = im

    return sky_areas

def validate_files(root_folder, image_folder, sky_areas, wavelengths, completed_file_name, errors_file_name):

    # remove areas that don't have all wavelengths
    invalid_sky_areas = validate_sky_area_wavelengths(
        root_folder, image_folder, sky_areas, wavelengths, errors_file_name)

    # remove areas that have already been processed
    process_sky_areas = remove_already_processed_sky_areas(root_folder, sky_areas, completed_file_name)


def check_output_folders(root_folder):
    logger.info("Checking folders")
    #if not os.path.isdir(root_folder + '/output'):
    #    os.makedirs(root_folder + '/output')
    #    logger.info("Creating output folder")
    #if not os.path.isdir(root_folder + '/log'):
    #    os.makedirs(root_folder + '/log')
    #    logger.info("Creating log folder")
    logger.info("Finished checking folders")

def get_bounding_box(sky_area, fits_image_shape, window_size, stride):

    rect = []
    if sky_area.field_rect is None:
        rect = FieldRect(0, fits_image_shape[0], 0, fits_image_shape[1])
    else:
        rect = sky_area.field_rect

    field_bb = boundingbox.BoundingBox(
        left=rect.left+window_size, right=rect.right-window_size,
        top=rect.top-window_size, bottom=rect.bottom+window_size, step=stride)

    return field_bb


def process(options, feature_factory):

    root_folder = options.root_folder
    image_folder = options.image_folder_path
    index = options.index
    required_wavelengths=options.required_wavelengths

    sky_areas_file_name = 'sky_areas_{0}.txt'.format(index)
    images_file_name = 'image_files_{0}.txt'.format(index)
    completed_file_name = 'processed_{0}.txt'.format(index)
    errors_file_name = 'errors_{0}.txt'.format(index)

    check_output_folders(root_folder)

    # id, field, wavelength, sigma_patch, file_path
    # remove any that don't have images in all wavelengths, or those that have already been processed
    sky_areas = load_sky_areas(root_folder, sky_areas_file_name, images_file_name, required_wavelengths)
    validate_files(root_folder, image_folder, sky_areas, required_wavelengths, completed_file_name, errors_file_name)

    # process each sky area, listed in the general text file, one at a time
    for sky_area_id, sky_area in sky_areas.items():

        # open fits files for sky area
        fh = fitshelper.FitsHelper(
            logger, image_folder, sky_area.image_files, required_wavelengths, sky_area.field_rect, use_mem_map=False)

        # calc background levels for each image file
        calc_background_sigma_levels(options, sky_area, sky_area.image_files, fh)

        # assume all the wavelengths fits data are the same size
        field_bb = get_bounding_box(sky_area, fh.get_image_shape(), options.window_size, options.stride)

        # get the patches/sub images, positions and offsets (if multiple fields)
        patch_factory = PatchFactory(logger, fh, feature_factory)
        gen_samples, gen_positions = patch_factory.get_features_all_pixels(options, field_bb, sky_area.image_files)

        output_folder_path = options.output_folder_path + str(sky_area_id) + '/'

        # create output dir
        if not os.path.isdir(output_folder_path):
            os.makedirs(output_folder_path)

        logger.info("saving raw samples and positions for: {0}".format(sky_area_id))
        numpy.savetxt(output_folder_path + "samples.csv", gen_samples, delimiter=",")
        save_hd5(output_folder_path + "samples.hd5", gen_samples, data_name='samples')
        numpy.savetxt(output_folder_path + "positions.csv", gen_positions, delimiter=",", fmt="%i")

        logger.info("create sigma lists for object detection for: ".format(sky_area_id))

        create_mask_files(options, output_folder_path, fh,
                          sky_area.image_files, gen_positions, options.index, options.prefix)

        fh.close()
        del fh
        del patch_factory
        del gen_positions
        del gen_samples

        with open(root_folder + completed_file_name, "a") as comp_file:
            comp_file.write("{0}\r\n".format(sky_area_id))
            comp_file.close()

        logger.info("Finished creating features for: {0}".format(sky_area_id))

def save_hd5(file_name, data, data_name='samples'):
    f = h5py.File(file_name, "w")
    f.attrs['creator'] = 'alex'
    f.attrs['test number'] = 'zz'
    f.attrs['HDF5_Version'] = h5py.version.hdf5_version
    f.attrs['h5py_version'] = h5py.version.version

    entry = f.create_group('entry')
    entry.attrs['default'] = 'data'
    entry.create_dataset('title', data='1-D scan of I00 v. mr')

    # write the data
    ds = entry.create_dataset(data_name, data=data)
    ds.attrs['units'] = 'test data'
    ds.attrs['long_name'] = 'test data for saving'

    f.close()
    del f

    print ("wrote file:", file_name)


def run(options):

    #options = FeatureOptions(config)
    #options.print_options()

    #options.radial_width = 1
    #options.window_size = 10
    #options.stride = 1

    options.patch_shape = numpy.array([options.window_size*2, options.window_size*2])

    feature_factory = PowerSpectrumFeature(options.patch_shape, options.radial_width)

    process(options, feature_factory)

# #######################################################################################
# # Main
# #######################################################################################


class FeatureOptions(object):

    def __init__(self, config):

        self.test_name = config['test_name']
        self.index = config['index']
        self.root_folder = config['root_folder']
        self.image_folder_path = config['image_folder']
        self.output_folder_path = self.root_folder + '/' + self.test_name + '/output_' + str(self.index) + '/'

        self.log_folder = self.output_folder_path + '/log/'
        if not os.path.isdir(self.log_folder):
            os.makedirs(self.log_folder)
        self.log_file_name = '/feature_extraction_log_{0}_{1}_{2}.txt'.format(
            config['test_name'], config['index'], strftime('%H_%M_%S', gmtime()))

        self.required_wavelengths = config['required_wavelengths']
        print(self.required_wavelengths)

        self.required_wavelengths.sort()  # sort to ensure always same order
        self.stride = int(config['stride'])
        if self.test_name.startswith('ps'):
            self.radial_width = int(config['radial_width'])
        self.window_size = int(config['window_size'])
        self.prefix = "gen"
        self.suffix = "_" + str(self.index)
        self.min_sigma_multiplier = int(config['min_sigma_multiplier'])
        self.RAW_SAMPLES_FILENAME = "/{0}_raw_samples{1}.csv".format(self.prefix, self.suffix)
        self.POSITIONS_FILENAME = "/{0}_positions{1}.csv".format(self.prefix, self.suffix)
        self.NORM_LOG_SAMPLES_FILENAME = "/{0}_normalized_logged_samples{1}.csv".format(self.prefix, self.suffix)
        self.LOGGED_SAMPLES_FILENAME = "/{0}_logged_samples{1}.csv".format(self.prefix, self.suffix)
        self.PCA_PLOT_FILENAME = "/{0}_normed_logged_samples_pca{1}.png".format(self.prefix, self.suffix)

        self.sigma_clip = 3 #config['sigma_clip']
        self.sigma_clip_iterations = 10 #config['sigma_iterations']
        self.sigma_multipliers = config['sigma_multipliers']
        #self.stride = 1

    def print_options(self):
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        for attr in attributes:
            k = attr[0]
            v = attr[1]
            if k.startswith('_'):
                continue
            logger.info("{0} : {1} ".format(k, v))

logger = None


if __name__ == "__main__":

    config = cf.get_config(sys.argv)
    options = FeatureOptions(config)
    log.configure_logging(options.log_folder + options.log_file_name)
    logger = log.get_logger("feature_extraction_" + str(config['index']) + config['test_name'])
    options.print_options()

    logger.debug("*** Starting ***")
    #try:
    run(options)
    #except Exception as excep:
    #    logger.error(excep)
    logger.debug("*** Finished ***")

