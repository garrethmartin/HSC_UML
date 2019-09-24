__author__ = 'ah14aeb'
import numpy as np
import sys
import config
import log
from astropy.io import fits as pyfits

def main(config):
    image_folder = '/home/ah14aeb/Downloads/hst_images/macs1149/'
    conn_cat_path = '/home/ah14aeb/Dropbox/sersic_cas_gini_m20/5sig_nobin_15_11/macs1149'
    conn_cat = np.loadtxt(conn_cat_path + '/object_catalogue.txt', delimiter=" ", dtype=np.int)

    long_hdu = pyfits.open(image_folder + 'hlsp_frontier_hst_acs-30mas_macs1149_f814w_v1.0-epoch2_drz.fits')
    long_image = long_hdu[0].data

    short_hdu = pyfits.open(image_folder + 'hlsp_frontier_hst_acs-30mas_macs1149_f435w_v1.0-epoch2_drz.fits')
    short_image = short_hdu[0].data

    xv = conn_cat[:, 8]
    yv = conn_cat[:, 9]

    long_pixel_values = long_image[yv, xv]
    short_pixel_values = short_image[yv, xv]

    #f814w=0.00127304950729
    #f606w=0.00132143159863
    #f435w=0.000719556468539

    #macs0717
    #long_sigma = 0.000974692462478
    #short_sigma = 0.000729420571588

    #macs1149
    long_sigma=0.00072327000089
    short_sigma=0.00071105902316

    long_5sigma = (long_pixel_values > (5*long_sigma))*1
    long_10sigma = (long_pixel_values > (10*long_sigma))*1
    long_15sigma = (long_pixel_values > (15*long_sigma))*1

    short_5sigma = (short_pixel_values > (5*short_sigma)) *1
    short_10sigma = (short_pixel_values > (10*short_sigma))*1
    short_15sigma = (short_pixel_values > (15*short_sigma))*1


    result = np.c_[conn_cat, long_5sigma, long_10sigma, long_15sigma, short_5sigma, short_10sigma, short_15sigma]

    np.savetxt(conn_cat_path + '/object_catalogue_with_sigmas.txt', result, delimiter=" ", fmt="%i")


########################################################################################
# Main
########################################################################################

logger = None

if __name__ == "__main__":

    config = None
    #config.get_config(sys.argv)
    #log.configure_logging(config['log_file_path'])
    #logger = log.get_logger("object sigmas")

    #logger.debug("*** Starting ***")
    main(config)
    #logger.debug("*** Finished ***")
