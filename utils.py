# Company: Sandia National Labs
# Author: Mike Metral
# Email: mdmetra@sandia.gov
# Date: 03/14/12

import os
import sys
import logging
import logging_colorer

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

class Utils:
#-------------------------------------------------------------------------------
    @staticmethod
    def set_logging(logging_level):
        logging.basicConfig(level=logging_level,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
#-------------------------------------------------------------------------------
    @staticmethod
    def get_dir_files(directory):
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
    def plot_data(x, y, plot_title, filepath):
        dots = []
    
        if len(x) == len(y):
            for i in range(0, len(x)):
                dot = [ x[i], y[i] ]
                dots.append(dot)
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
        plt.plot(*zip(*dots), marker='o', color='r', ls='')

        # Append .png if no extension given
        if not filepath.endswith('.png') and \
            not filepath.endswith('.pdf') and \
            not filepath.endswith('.svg') :
                filepath += '.png'

        logging.info("-------------------------------------------------")
        logging.info("Saving graph to: " + filepath) 
        plt.savefig(filepath)
#-------------------------------------------------------------------------------
