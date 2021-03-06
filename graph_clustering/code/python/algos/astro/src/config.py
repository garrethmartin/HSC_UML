__author__ = 'ah14aeb'
from configobj import ConfigObj, ConfigObjError
import argparse

def get_config(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="the config file path")
    parser.add_argument("-f", "--testname", help="used as the output foldername")
    parser.add_argument("-w", "--windowsize", help="the window size, overrides value in config file", type=int)
    parser.add_argument("-r", "--radialbinsize", help="the radial bin size, overrides value in the config file", type=int)
    parser.add_argument("-s", "--stride", help="the stride, overrides value in the config file", type=int)
    parser.add_argument("-i", "--index",
                        help="the index of the inputs files to process, overrides value in the config file", type=int)
    parser.add_argument("-x", "--folder", help="root folder", type=str)
    parser.add_argument("-t", "--imagefolder", type=str)
    parser.add_argument("-c", "--nthreads", type=int)


    args = parser.parse_args()

    config_file_name = args.config_file

    # load config file
    config = None
    try:
        config = ConfigObj(config_file_name, file_error=True)
        config.interpolation = True

        if hasattr(args, 'testname'):
            config['test_name'] = args.testname
        if hasattr(args, 'index'):
            config['index'] = args.index
        if hasattr(args, 'windowsize'):
            config['window_size'] = args.windowsize
        if hasattr(args, 'radialbinsize'):
            config['radial_width'] = args.radialbinsize
        if hasattr(args, 'stride'):
            config['stride'] = args.stride
        if hasattr(args, 'folder'):
            config['root_folder'] = args.folder
        if hasattr(args, 'imagefolder'):
            config['image_folder'] = args.imagefolder
        if hasattr(args, 'nthreads'):
            config['n_threads'] = args.nthreads

    except (ConfigObjError, IOError) as e:
        print("Error could not read {0}: {1}".format(config_file_name, e))
        exit(1)

    return config
