import pandas as pd
import numpy as np
import sys
import os
import re


def get_images(folder, regex):

    image_files = {}

    for file in os.listdir(folder):
        m = re.match(regex, file)
        if not m:
            print("error {0}".format(file))
            continue

        band = str(m.group(1))
        sky_region = str(m.group(2))

        if sky_region not in image_files:
            image_files[sky_region] = {}

        bands = image_files[sky_region]

        if band not in bands:
            bands[band] = file

    return image_files


def write_image_file(folder, image_files):

    header = 'id,sky_area_id,wavelength,file_name\n'
    counter = 0
    sky_area_counter = 0
    with open(folder + 'images.txt', 'w') as f:
        f.write(header)
        for area, bands in image_files.items():

            for wavelength, file_name in bands.items():
                line = "{},{},{},{}\r\n".format(counter, sky_area_counter, wavelength, file_name)
                f.write(line)
                counter += 1

            sky_area_counter += 1


def write_sky_area_file(folder, file_id, rows):

    header = 'id,field,field_rect,sigma_rect\n'
    file_path = folder + 'sky_areas_{}.txt'.format(file_id)

    with open(file_path, 'w') as f:
        f.write(header)

        sky_area_ids = rows['sky_area_id'].unique()
        for sky_area_id in sky_area_ids:
            f.write('{},None,None,None\n'.format(sky_area_id))


def write_sky_area_files(folder, data, sky_area_per_file=10):

    max_sky_areas = data['sky_area_id'].max()

    file_id = 0
    min = -1
    max = sky_area_per_file
    while min < (max_sky_areas + 1):

        mask = (data['sky_area_id'] > min) & (data['sky_area_id'] < max)

        rows = data[mask]

        write_sky_area_file(folder, file_id, rows)

        min += sky_area_per_file
        max += sky_area_per_file
        file_id += 1


def main(folder, regex):

    # create image_file config
    image_files = get_images(folder, regex)

    write_image_file(folder, image_files)

    data = pd.read_csv(folder + 'images.txt', delimiter=',')

    write_sky_area_files(folder, data)

    print(data['sky_area_id'])



if __name__ == "__main__":

    #regex = sys.argv[2]
    #regex = 'labels_([0-9]+)_([0-9]+)'
    regex = 'fpC-100006-([a-z0-9]+)-([0-9]+).fit'
    folder = 'E:/candels/stripe82/images/' # sys.argv[1]

    print("*** Starting ***")
    main(folder, regex)
    print("*** Finished ***")
