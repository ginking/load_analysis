import os
import sys
import logging
import logging_colorer

import matplotlib

# Agg allows plot creation if $DISPLAY env variable isn't set
matplotlib.use("Agg")

import matplotlib.pyplot as plt

class Utils:
    filepath = None
#-------------------------------------------------------------------------------
    @staticmethod
    def set_logging(logging_level):
        # Set up the logging configuration and format

        logging.basicConfig(level=logging_level,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

#-------------------------------------------------------------------------------
    @staticmethod
    def get_dir_listing(directory):
        # Iterates through the directory, extracting the filename of its files

        logging.debug("-------------------------------------------------")
        logging.debug("Listing directory: %s" % (directory))
        logging.debug("-----------------------------")

        dirlist = os.listdir(directory)
        filelist = []

        for i in dirlist:
            if os.path.isfile("%s/%s" % (directory,i)):
                logging.debug("Found file: %s%s", directory, i)
                filelist.append([directory, i])

        return filelist

#-------------------------------------------------------------------------------
    @staticmethod
    def fix_filepath(dirname, filename):
        # Properly prepends '/' before the filename to create a
        # properly formatted path with the dirname

        filepath = None

        if not dirname.endswith('/'):
            filepath = '/'.join([dirname,filename])
        else:
            filepath = ''.join([dirname,filename])

        return filepath

#-------------------------------------------------------------------------------
    @staticmethod
    def write_to_file(data):
        f = open(Utils.filepath, 'a+')
        f.write(data)
        f.close()

#-------------------------------------------------------------------------------
    @staticmethod
    def plot_data(x_axis, y_axis, plot_title, filepath):
        # Creates dot plot

        dot_pairs = []
    
        if len(x_axis) == len(y_axis):
            for i in range(0, len(x_axis)):
                dot = [ x_axis[i], y_axis[i] ]
                dot_pairs.append(dot)
        else:
            logging.error("-------------------------------------------------")
            logging.error("Mismatch in creating dot pairs!")
            sys.exit(0)

        logging.info("-------------------------------------------------")
        logging.info("Plotting data ...")

        plt.xlabel("Timestamps")
        plt.ylabel("Trimmed Deltas")
        plt.title(plot_title)

        # Create a dot plot
        plt.plot(*zip(*dot_pairs), marker='o', color='r', ls='')

        # Append .png if no extension given
        if not filepath.endswith('.png') and \
            not filepath.endswith('.pdf') and \
            not filepath.endswith('.svg') :
                filepath += '.png'

        logging.info("-------------------------------------------------")
        logging.info("Saving graph to: " + filepath) 
        plt.savefig(filepath)

#-------------------------------------------------------------------------------
