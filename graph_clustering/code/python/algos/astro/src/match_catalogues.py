import os
import sys
import collections
import numpy as np
import config
import log
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import metrics
from scipy.stats import pearsonr
from astropy import wcs
from astropy.io import fits as pyfits
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table as table

field_code = { 0: 'gn', 1 : 'uds', 2:'egs',3:'cos', 4:'gs'}
field_sizes = { 'gn' : [20480, 20480], 'gs' : [40500, 32400], 'egs' : [12600, 40800], 'cos' : [36000, 14000], 'uds' : [12800, 30720]}
field_offsets = {'gn' : [0,0], 'gs' : [0,0], 'egs' : [0,0], 'cos' : [0, 0], 'uds':[0,0]}

def combine_catalogues():
    # combine catalogues from each field
    root_folder = 'E:/kdata/candels/output_twocolor/catalogues/'
    a = table.read(root_folder + 'catalogue_all_with_notext.csv', format='csv')

    cat_keys = ['goodsn', 'uds', 'egs', 'cos', 'goodss']
    field_ids = [0,1,2,3,4]
    all = ['goodsn_matched.csv', 'uds_matched.csv', 'egs_matched.csv', 'cosmos_matched.csv', 'goodss_matched.csv']
    keys_sersic=['uds', 'cos', 'goods']
    field_ids_sersic=[1,3,4]
    with_sersic = ['uds_matched_with_sersic.csv', 'cosmos_matched_with_sersic.csv', 'goodss_matched_with_sersic.csv']

    #all = with_sersic
    #cat_keys = keys_sersic
    #field_ids = field_ids_sersic

    with open(root_folder + 'catalogue_all_with_notext.csv', mode="w") as cat_all:
        for i in range(len(all)):
            field_id = str(field_ids[i])
            field_name = cat_keys[i]
            cat_file_path = root_folder + all[i]
            print("{0} {1}".format(cat_file_path, field_id))
            cat_file = table.read(cat_file_path, format='csv')
            #cat_file = np.genfromtxt(cat_file_path, skip_header=1, delimiter=",")

            for i in range(len(cat_file)):
                #line = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15}".format(
                line = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}".format(
                    field_id, cat_file[i]['id_1'], cat_file[i]['label'], cat_file[i]['ra_1'], cat_file[i]['dec_1'],
                    cat_file[i]['numpixels'], cat_file[i]['w_h'], cat_file[i]['id_2'], cat_file[i]['ra_2'], cat_file[i]['dec_2'],
                    cat_file[i]['f_f160w'], cat_file[i]['f_f606w'], cat_file[i]['kron_radius'],
                    cat_file[i]['z_p']) #, cat_file[i]['col6'], cat_file[i]['col11'])  #col6 is galfit quality indicator, col11 sersic index
                cat_all.write(line)
                cat_all.write("\n")

field_cats = {
    0 : ['goodsn_3dhst.v4.1.cat.FITS', 'goodsn_3dhst.v4.1.zout.FITS'],
    1 : ['uds_3dhst.v4.2.cat.FITS', 'uds_3dhst.v4.2.zout.FITS'],
    2 : ['aegis_3dhst.v4.1.cat.FITS', 'aegis_3dhst.v4.1.zout.FITS'],
    3 : ['cosmos_3dhst.v4.1.cat.FITS', 'cosmos_3dhst.v4.1.zout.FITS'],
    4 : ['goodss_3dhst.v4.1.cat.FITS','goodss_3dhst.v4.1.zout.FITS']
}

field_cat_ids = {
    'goodsn' : 0,
    'uds' : 1,
    'egs' : 2,
    'cos' : 3,
    'goodss' : 4
}


def load_ml_catalogues(ml_root_folder):
    catalogues = {}
    for file_name in os.listdir(ml_root_folder):
        if not file_name.startswith('catalogue_'):
            continue
        cat = np.loadtxt(ml_root_folder + file_name, delimiter=",")
        cat_found = False
        for key, field_id in field_cat_ids.iteritems():
            if key in file_name:
                catalogues[field_id] = cat
                cat_found = True
                print ("loaded: {0}".format(key))
                break
        if cat_found == False:
            print("Error ml cat not found in cat ids:".format(file_name))
    return catalogues


def match_catalogues(ml_cat_root, catalog_root_folder):

    from astropy.coordinates import ICRS
    from astropy import units as u
    from astropy.coordinates import match_coordinates_sky

    print(ml_cat_root)
    # load ml catalogues #
    ml_catalogues = load_ml_catalogues(ml_cat_root)

    candels_cat = []

    # match each one to the photo and redshift catalogues
    for field_id, field_cat in field_cats.iteritems():

        photo_cat_file_name = catalog_root_folder + field_cat[0]
        z_cat_file_name = catalog_root_folder + field_cat[1]

        # load catalogues for fields ready for matching
        ml_cat = ml_catalogues[field_id]
        photo_cat = pyfits.open(photo_cat_file_name)
        z_cat = pyfits.open(z_cat_file_name)

        print("matching: {0} {1} {2}".format(field_id, photo_cat_file_name, z_cat_file_name))

        ml_ra = ml_cat[:, 4]
        ml_dec = ml_cat[:, 5]
        #photo_id = photo_cat[1].data['id']
        photo_ra = photo_cat[1].data['ra']
        photo_dec = photo_cat[1].data['dec']

        z_id = z_cat[1].data['id']
        z_p = z_cat[1].data['z_p']

        new_cat = []
        #assume ra1/dec1 and ra/dec2 are arrays loaded from some file
        ml_cat_coords = ICRS(ml_ra, ml_dec, unit=(u.degree, u.degree))
        photo_cat_coords = ICRS(photo_ra, photo_dec, unit=(u.degree, u.degree))
        idx, d2d, d3d = photo_cat_coords.match_to_catalog_sky(ml_cat_coords)

        photo_cat_data = photo_cat[1].data
        z_cat_data = z_cat[1].data
        cols_names = photo_cat[1].data.columns.names
        use_f606 = False
        use_f814 = False
        use_f125 = False
        use_f435 = False
        if 'f_f606w' in cols_names:
            use_f606 = True
        if 'f_f814w' in cols_names:
            use_f814 = True
        if 'f_f435w' in cols_names:
            use_f435 = True
        if 'f_f125w' in cols_names:
            use_f125 = True

        for i in range(idx.shape[0]):
        #for i in range(2000):
            if d2d[i].arcsecond > 1:
                # skip object from photometry if no match within 1 arcsecond
                # i.e. assume it is a duff detection in the ml_cat
                continue

            photo_id = i
            ml_id = idx[i]

            mlr = ml_cat[ml_id, :]
            pr = photo_cat_data[photo_id]
            prid = photo_cat_data['id'][photo_id]
            zr = z_cat_data[z_id == prid]
            z_p = zr['z_p'][0]

            f_f606w = -99.0
            f_f814w = -99.0
            f_f435w = -99.0
            f_f125w = -99.0
            if use_f606:
                f_f606w = pr['f_f606w']
            if use_f814:
                f_f814w = pr['f_f814w']
            if use_f435:
                f_f435w = pr['f_f435w']
            if use_f125:
                f_f125w = pr['f_f125w']

            new_row = [field_id, int(mlr[0]), int(mlr[1]), int(mlr[2]), int(mlr[3]), format(mlr[4]), format(mlr[5]), int(mlr[6]),
                       int(mlr[7]),
                       int(pr['id']), format(pr['x']), format(pr['y']), format(pr['ra']), format(pr['dec']), pr['f_f160w'],
                       f_f125w, f_f814w, f_f606w, f_f435w, pr['kron_radius'],
                        z_p]

            if i % 1000 == 0:
                print "idx {0}".format(i)
            new_cat.append(new_row)
            candels_cat.append(new_row)
        #idx2, d2d2, d3d2 = ml_cat_coords.match_to_catalog_sky(photo_cat_coords)

        print("saving text")
        print("f {0}".format(str(field_code[field_id])))
        if len(new_cat) > 0:
            print(new_cat[0])
            np.savetxt(ml_cat_root + str(field_code[field_id]) + '_matches.csv', new_cat, delimiter=",", fmt="%s")

        print("hi")

        #idx, d2d, d3d = match_coordinates_sky(c1, catalog)  # same thing

    np.savetxt(ml_cat_root + 'candels_matches.csv', candels_cat, delimiter=",", fmt="%s")


def main():

    root_folder = 'e:/kdata/candels3/' #sys.argv[2]
    test_folder = root_folder + 'twocolor/model_all_4/' #sys.argv[3]
    output_folder = test_folder + 'catalogs/' #+ 'final/catalogs/' #'output_two_color_test2/'
    image_folder = 'M:/kdata/candels/'
    offset = 2

    class_file_name = test_folder + 'agg_multi_classifications_labels_200_60_1174.txt' #'agg_multi_classifications_labels_120_100_1174.txt' #'kmeans_classifications_labels_100_20_1827.txt'
    prox_file_name = test_folder + 'agg_multi_silhouette_values_200_60_1174.txt'#'agg_multi_silhouette_values_120_100_1174.txt'
    #convert_cat_add_ra_dec_in_degrees(
    #    root_folder, test_folder, output_folder, image_folder, class_file_name, prox_file_name, offset)

    create_final_galaxy_zoo_catalogue(output_folder, test_folder, class_file_name, prox_file_name)

    ml_cat_root = output_folder #'E:/kdata/candels/output_twocolor_test/'
    photo_cat_root = 'M:/kdata/candels/3d_catalogues/cats/'
    # match catalogues
    #match_catalogues(ml_cat_root, photo_cat_root)

    #create_final_catalogue(output_folder, test_folder, class_file_name, prox_file_name)

def main2():
    root_folder = 'e:/kdata/candels3/' #sys.argv[2]
    test_folder = root_folder + 'twocolor/model_all_10/' #sys.argv[3]
    output_folder = test_folder + 'catalogs/' #+ 'final/catalogs/' #'output_two_color_test2/'
    image_folder = 'M:/kdata/candels/'
    offset = 2

    class_file_name = test_folder + 'agg_multi_classifications_labels_120_100_1174.txt' #'kmeans_classifications_labels_100_20_1827.txt'
    prox_file_name = test_folder + 'agg_multi_silhouette_values_120_100_1174.txt'

    create_final_catalogue(output_folder, test_folder, class_file_name, prox_file_name)

def create_final_catalogue(output_folder, test_folder, class_file_name, prox_file_name):

    cat_all = np.loadtxt(output_folder + 'candels_matches.csv', delimiter=",", skiprows=1)

    # field_id,obj_id,class_id,x,y,ra_img,dec_img,num_pixels,wh, p_obj_id, p_x, p_y, p_ra, p_dec, f_f160w, f_f125w, f_814w, f_f606w, f_f435w, kron_radius, p_z
    # 0,92048,2,12535,1579,189.150473,62.094192,4,30,3,12537.001,1584.393,189.150401,62.094282,-99.0,-99.0,-99.0,-99.0,-99.0,0.0,-99.0
    print("loading classifications: {0}".format(class_file_name))
    labels = np.loadtxt(class_file_name, dtype=np.int, delimiter=',')

    print("loading proximities: {0}".format(prox_file_name))
    proximities = np.loadtxt(prox_file_name, dtype=np.float32, delimiter=',')

    # split catalogue into fields dictionary
    cat_fields = get_field_rows(cat_all)
    label_fields = get_field_rows(labels)
    proximities_fields = get_field_rows(proximities)

    final_cat = []
    final_cat2 = []

    f6 = lambda x: "%.6f" % x
    f3 = lambda x: "%.3f" % x
    f1 = lambda x: "%.1f" % x

    for field_id, field_rows in cat_fields.iteritems():

        label_rows = label_fields[field_id]
        proximity_rows = proximities_fields[field_id]

        for i in range(field_rows.shape[0]):
            fr = field_rows[i]

            obj_id = fr[1]
            label_row = label_rows[label_rows[:, 2] == obj_id]
            prox_row = proximity_rows[proximity_rows[:, 2] == obj_id]

            labels = label_row[0][3:]
            proxes = prox_row[0][3:]
            labels = [int(x) for x in labels.tolist()]
            proxes = [round(x, 5) for x in proxes.tolist()]

            ra = fr[5]
            dec = fr[6]
            x = fr[3]
            y = fr[4]

            num_pixels = fr[7]
            wh = fr[8]

            class_id = fr[2]
            if class_id != labels[0]:
                print("error: {} {}".format(class_id, labels[0]))
            p_obj_id = fr[9]
            p_x = fr[10]
            p_y = fr[11]
            p_ra = fr[12]
            p_dec = fr[13]


            new_cat_row = [int(field_id), int(p_obj_id), f3(p_x), f3(p_y), f6(p_ra), f6(p_dec)] + labels + proxes
            new_cat_row2 = [int(field_id), int(num_pixels), int(wh), int(obj_id), int(x), int(y), f6(ra), f6(dec), int(p_obj_id), f3(p_x), f3(p_y), f6(p_ra), f6(p_dec)] + \
                           labels + proxes

            final_cat.append(new_cat_row)
            final_cat2.append(new_cat_row2)

    #np.savetxt(ml_cat_root + 'candels_matches.csv', candels_cat, delimiter=",", fmt="%s")
    np.savetxt(output_folder + "final_catalogue.csv", final_cat, delimiter=",", fmt="%s")
    np.savetxt(output_folder + "final_catalogue_debug.csv", final_cat2, delimiter=",", fmt="%s")


def create_final_galaxy_zoo_catalogue(output_folder, test_folder, class_file_name, prox_file_name):

    cat_all = np.loadtxt(output_folder + 'catalogue_all.csv', delimiter=",")

    # field_id, obj_id, classification, obj_x, obj_y, ra, dec, num_pixels, width, height
    #0, 3, 7, 1033, 11597, 189.561903, 62.260781, 12, 68, 68
    #0, 4, 0, 1017, 11641, 189.562484, 62.261513, 3, 21, 21

    print("loading classifications: {0}".format(class_file_name))
    labels = np.loadtxt(class_file_name, dtype=np.int, delimiter=',')

    print("loading proximities: {0}".format(prox_file_name))
    proximities = np.loadtxt(prox_file_name, dtype=np.float32, delimiter=',')

    # split catalogue into fields dictionary
    cat_fields = get_field_rows(cat_all)
    label_fields = get_field_rows(labels)
    proximities_fields = get_field_rows(proximities)

    final_cat = []
    final_cat2 = []

    f6 = lambda x: "%.6f" % x
    f3 = lambda x: "%.3f" % x
    f1 = lambda x: "%.1f" % x

    for field_id, field_rows in cat_fields.iteritems():

        label_rows = label_fields[field_id]
        proximity_rows = proximities_fields[field_id]

        for i in range(field_rows.shape[0]):
            fr = field_rows[i]
            if field_id != fr[0]:
                print("field error {} {}".format(field_id, fr[0]))

            obj_id = fr[1]
            label_row = label_rows[label_rows[:, 2] == obj_id]
            prox_row = proximity_rows[proximity_rows[:, 2] == obj_id]

            labels = label_row[0][3:]
            proxes = prox_row[0][3:]
            labels = [int(x) for x in labels.tolist()]
            proxes = [round(x, 5) for x in proxes.tolist()]

            ra = fr[5]
            dec = fr[6]
            x = fr[3]
            y = fr[4]

            num_pixels = fr[7]
            wh = fr[8]

            class_id = fr[2]
            if class_id != labels[0]:
                print("error: {} {}".format(class_id, labels[0]))

            new_cat_row2 = [int(field_id), int(num_pixels), int(wh), int(obj_id), int(x), int(y), f6(ra), f6(dec)] + \
                           labels + proxes

            final_cat2.append(new_cat_row2)

    np.savetxt(output_folder + "final_gz_catalogue_debug.csv", final_cat2, delimiter=",", fmt="%s")


def get_field_rows(cat_all):
    fields = {}
    field_id = 0
    max_field_id = cat_all[:,0].max() + 1
    while field_id < max_field_id:
        field_rows = cat_all[cat_all[:, 0] == field_id]
        fields[field_id] = field_rows
        field_id += 1
    return fields


def main2():

    root_folder = 'e:/kdata/candels3/' #sys.argv[2]
    test_folder = root_folder + 'twocolor/model_all_10/' #sys.argv[3]
    output_folder = test_folder + 'catalogs/' #+ 'final/catalogs/' #'output_two_color_test2/'

    ml_cat_root = output_folder #'E:/kdata/candels/output_twocolor_test/'
    photo_cat_root = 'M:/kdata/candels/3d_catalogues/cats/'
    # match catalogues
    match_catalogues(ml_cat_root, photo_cat_root)


def convert_cat_add_ra_dec_in_degrees(
        root_folder, test_folder, output_folder, image_folder, class_file_name, prox_file_name, offset):

    Field = collections.namedtuple('Field', 'id name fits_file shape offset')
    fields = {}

    fields[0] = Field(0, 'goodsn', '/goodsn/hlsp_candels_hst_wfc3_gn-tot-60mas_f160w_v1.0_drz.fits', [20480, 20480], [0, 0])
    fields[1] = Field(1, 'uds', 'hlsp_candels_hst_wfc3_uds-tot_f160w_v1.0_drz.fits', [12800, 30720], [0, 0])
    fields[2] = Field(2, 'egs', 'hlsp_candels_hst_wfc3_egs-tot-60mas_f160w_v1.0_drz.fits', [12600, 40800], [0, 0])
    fields[3] = Field(3, 'cos', 'hlsp_candels_hst_wfc3_cos-tot_f160w_v1.0_drz.fits', [36000, 14000], [0, 0])
    fields[4] = Field(4, 'goodss', '/goodss/hlsp_candels_hst_wfc3_gs-tot_f160w_v1.0_drz.fits', [16500, 15300], [12000, 28500, 7000, 22300]) #[40500, 32400]
    # goods south cutout left=7000 right=22300 bottom=12000 top=28500

    # 1 g:\projects\FrontierFields\ \rift_8_8_2_3\model_5000\pearson\ 10
    #training_image_index = '0' #sys.argv[1]
    #root_folder = 'e:/kdata/candels/' #sys.argv[2]
    #test_folder = root_folder + 'twocolor/model_all/' #sys.argv[3]
    #image_folder = 'M:/kdata/candels/'
    #offset = 2

    #class_file_name = test_folder + 'kmeans_classifications_labels_100_35_1827.txt'

    # get degrees of objects, and parameters. We want field, object, x, y, ra/dec in degrees, classification

    # load catalogue
    # load classifications
    # iterate
        # identify field
        # load fits file for field to get header and WCS
        # get catalogue for field
        # get ra and dec in degrees and sky coords
        # save ra and dec to catalogue with wanted columns
        # save new catagloeu with ra,dec and classification
        # save catalgoeu with hours minutes seconds

    # output catalgoue + deg and hms + id from external + classification

    print("loading catalogue files: {0}".format(test_folder))
    catalogues = load_files(test_folder)

    print("loading classifications: {0}".format(class_file_name))
    labels = np.loadtxt(class_file_name, dtype=np.int, delimiter=',')

    print("loading proximities: {0}".format(prox_file_name))
    proximities = np.loadtxt(prox_file_name, dtype=np.int, delimiter=',')

    #output_folder = root_folder + 'output_twocolor'
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    print("output_folder: {0}".format(output_folder))

    new_catalogues = process_catalogues(image_folder, output_folder, catalogues, fields, labels, proximities, offset)

    #match_catalogues(new_catalogues)


def process_catalogues(image_folder, output_folder, catalogue, fields, labels, proximities, offset):
    # identify field
    # load fits file for field to get header and WCS
    # get catalogue for field
    # get ra and dec in degrees and sky coords
    # save ra and dec to catalogue with wanted columns
    # save new catagloeu with ra,dec and classification
    # save catalgoeu with hours minutes seconds

    catalogues = {}
    all_catalogue = None
    for field_id, field_obj in fields.iteritems():
        fits_file_path = image_folder + field_obj.fits_file
        hdulist = pyfits.open(fits_file_path)
        w = wcs.WCS(hdulist[0].header)
        hdulist.close()

        field_col = 0
        object_id_col = 2
        label_col = 3

        field_labels = labels[labels[:, field_col] == field_id]
        field_proximity = proximities[proximities[:, field_col] == field_id]
        field_catalogue = catalogue[catalogue[:, field_col] == field_id]

        new_field_catalogue, new_cat_sky_coords = process_field(
            field_obj, field_labels, field_proximity, field_catalogue, w, offset)

        output_file_name = '/catalogue_{0}.csv'.format(field_obj.name)
        np.savetxt(output_folder + output_file_name, new_field_catalogue,
                   fmt="%i, %i, %i, %i, %f, %f, %i, %i, %i", delimiter=",")
        #output_file_name = 'sky_coords_{0}.csv'.format(field_obj.name)
        #np.savetxt(output_folder + output_file_name, new_cat_sky_coords, fmt="%i, %i, %i, %i, %f, %f, %s, %s", delimiter=",")
        #   obj_id, classification, obj_x, obj_y, ra, dec, ra_hms, dec_dms

        #new_cat.append([obj_id, obj_x, obj_y, ra, dec, num_pixels, width, height])
        #new_cat_hhmmss.append([obj_id, obj_x, obj_y, ra, dec, s.to_string('hmsdms')])

        catalogues[field_id] = new_field_catalogue

        field_col = np.zeros(len(new_field_catalogue))
        field_col[:] = field_id
        new_field_catalogue = np.c_[field_col, np.array(new_field_catalogue)]
        if all_catalogue is None:
            all_catalogue = new_field_catalogue
        else:
            all_catalogue = np.vstack((all_catalogue, new_field_catalogue))

    output_file_name = 'catalogue_all.csv'
    np.savetxt(output_folder + output_file_name, all_catalogue, fmt="%i, %i, %i, %i, %i, %f, %f, %i, %i, %i", delimiter=",")

    return catalogues


def process_field(field_obj, labels, proximities, catalogue, world_coords, offset):

    new_cat = []
    new_cat_hhmmss = []
    for i in range(catalogue.shape[0]):
    #for i in range(100):

        galaxy = catalogue[i, offset:]
        obj_id = int(galaxy[0])
        if int(obj_id) == 4509:
            print "here"
        num_pixels = galaxy[1]
        width = galaxy[2]  # from bounding rect curr square
        height = galaxy[3] # from bounding rect curr square
        # co = cut out (currently square)
        co_left = galaxy[4]
        co_right = galaxy[5]
        co_top = galaxy[6]
        co_bottom = galaxy[7]

        obj_x = galaxy[8]
        obj_y = galaxy[9]

        # br = bounding rect (currently square)
        br_left = galaxy[10]
        br_right = galaxy[11]
        br_top = galaxy[12]
        br_bottom = galaxy[13]

        world = world_coords.wcs_pix2world([[obj_x, obj_y]], 1)  #x first y second
        pixcrd2 = world_coords.wcs_world2pix(world, 1)
        #ra:  2:17:06.2
        #dec: -5:13:17.6
        ra = world[0][0]
        dec = world[0][1]
        s = SkyCoord(world[0][0], world[0][1], unit='deg')
        #print "{0} {1} {2}".format(obj_id, world, s.to_string('hmsdms'))

        hmsdms = s.to_string('hmsdms').split(' ')
        ra_hms = hmsdms[0]
        dec_dms = hmsdms[1]
        classification = labels[labels[:, 2] == obj_id][0][3]

        new_cat.append([obj_id, classification, obj_x, obj_y, ra, dec, num_pixels, width, height])
        new_cat_hhmmss.append([obj_id, classification, obj_x, obj_y, ra, dec, ra_hms, dec_dms])

    return new_cat, new_cat_hhmmss


def load_files(model_folder):

    print("loading sparse count files from: {0}".format(model_folder))

    count_file_contents = []
    for file_name in os.listdir(model_folder):
        if not file_name.startswith('complete_object_catalogue_'):
            continue

        print("adding: {0}".format(file_name))
        contents = np.loadtxt(model_folder + file_name, delimiter=' ', dtype=np.float32)
        count_file_contents.append(contents)

    all_object_counts = count_file_contents[0]
    for i in range(1, len(count_file_contents), 1):
        all_object_counts = np.append(all_object_counts, count_file_contents[i], axis=0)

    #print("saving all sparse counts")
    #np.savetxt(model_folder + 'all_sparse_counts.txt', all_object_counts, fmt="%d", delimiter=",")

    return all_object_counts

########################################################################################
# Main
########################################################################################

if __name__ == "__main__":
    main()

"""
    # prob

    (274/36000) * (273/35999) * (272/35998) or (274/36000) * (274/35999) * (274/35998)

    num_true = 0
    ids = [10, 33000, 23434]

    for i in range(10000000):
        ids = np.random.random_integers(0, 36000, 3)
        ints = np.random.random_integers(0, 36000, 274)
        count = 0

        for id in ids:
            if id in ints:
                count +=1

        if count == 3:
            num_true += 1
            print "true: {0}".format(i)
        #if count == 2:
        #    print "two"
        if i % 100000 == 0:
            print "mod: {0}".format(i)

    print (num_true)





    # pymorph code
    size = [0, 1, 9, 1, 120]
    searchrad = '0.2arc'

                # Determine Search Radius
                try:
                    SearchRad = c.searchrad
                except:
                    if RaDecInfo:
                        SearchRad = '1arc'
                        print 'No search radius found. Setting to 1 arc sec'
                    else:
                        SearchRad = '10pix'
                        print 'No search radius found. Setting to 10 pix'
                if SearchRad.endswith('arc'):
                    SeaDeg = float(SearchRad[:-3]) / (60.0 * 60.0)
                    SeaPix = 10.0
                elif SearchRad.endswith('pix'):
                    SeaPix = float(SearchRad[:-3])
                    SeaDeg = c.pixelscale * SeaPix  / (60.0 * 60.0)

                # first count the number of "potential" targets in the search radius
                c.SexTargets = 0
                good_objects = []
                bad_objects = []
                good_distance = []
                bad_distance = []
                good_object = ''

                os.system('cp %s sex_%s.txt' %(sex_cata, c.fstring))

                center_distance = 999.0 #the distance from the center to the best target
                for line_s in open(sex_cata, 'r'):

                    try:
                        values = line_s.split()
                        alpha_s = float(values[3])
                        delta_s = float(values[4])
                        if RaDecInfo == 0:
                            alpha_s = 9999
                            delta_s = 9999
                        sex_id = values[0]
                        xcntr  = float(values[1])
                        ycntr  = float(values[2])

                        if(abs(alpha_j - alpha_s) < SeaDeg and \
                           abs(delta_s - delta_j) < SeaDeg or \
                           abs(xcntr - ximg) < SeaPix and \
                           abs(ycntr - yimg) < SeaPix):
                            curr_distance = np.sqrt(np.min([(xcntr - ximg)**2+(ycntr - yimg)**2,(alpha_j - alpha_s)**2+(delta_s - delta_j)**2]))
                            print "Candidate distance: %.3f" %curr_distance
                            c.SexTargets +=1
                            if curr_distance < center_distance:
                                center_distance = curr_distance
                                print "New Preferred target!!"
                                good_object = line_s
                            print "Target distance: %.3f" %center_distance
                    except:
                        if values[0].strip().isdigit():
                            print 'Something happend in the pipeline. ' + \

def pearson3(a, b):
    r, _ = pearsonr(a, b)
    return 1 - r

def pearson_affinity(M):
   return 1 - np.array([[pearsonr(a,b)[0] for a in M] for b in M])

def load_and_normalize(counts, min_patches, offset=1):
    indices = []
    rows = counts.shape[0]
    #cols = counts.shape[1] - offset

    for i in range(rows):
        if np.sum(counts[i, offset:]) > min_patches:
            indices.append(i)
    indices = np.array(indices)

    large_counts = counts[indices, :]

    print("tfidf normalizing data")
    samples = large_counts[:, offset:] ## remove object column
    samples = samples.astype(np.float32)
    #samples = normalize_rows(samples)

    a = TfidfTransformer()
    samples = a.fit_transform(samples)

    return large_counts, samples.toarray()

def get_ra_dec(fits_file_path, unsup_cat, offset):

    hdulist = pyfits.open(fits_file_path)
    w = wcs.WCS(hdulist[0].header)

    for i in range(unsup_cat.shape[0]):
        galaxy = unsup_cat[i, offset:]
        obj_id = galaxy[0]
        if int(obj_id) == 4509:
            print "here"
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


        world = w.wcs_pix2world([[obj_x, obj_y]], 1)  #x first y second
        pixcrd2 = w.wcs_world2pix(world, 1)
        #ra:  2:17:06.2
        #dec: -5:13:17.6
        s = SkyCoord(world[0][0], world[0][1], unit='deg')
        print "{0} {1} {2}".format(obj_id, world, s.to_string('hmsdms'))

        print(world)

"""


"""



    numcols = 0
    oldcols = 0
    with open(root_folder + 'catalogue_all_with_notext.csv', mode="w") as cat_all:

        for i in range(len(all)):
            field_id = str(field_ids[i])
            field_name = cat_keys[i]
            cat_file_path = root_folder + all[i]
            with open(cat_file_path) as cat_file:
                line_iter = 0
                for line in cat_file:
                    if "numpixels" in line:
                        continue

                    cols = line.split(",")
                    numcols = len(cols)
                    if oldcols == 0:
                        oldcols = numcols

                    #if oldcols != numcols:
                    #    print("i {0} line_iter {1} cols {2} oldcols {3}".format(i, line_iter, numcols, oldcols))
                    #new_line = field_id + ',' + field_name + ',' + line
                    new_line = field_id + ',' + line
                    cat_all.write(new_line)
                    line_iter += 1

                cat_file.close()
            if oldcols != numcols:
                print ("i {0} oldcols: {1} numcols {2}".format(i, oldcols, numcols))

            oldcols = numcols
        cat_all.close()
"""