import os
import sys
import logging
import logging_colorer

class Utils:
    def set_logging(self, logging_level):
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
