#!/usr/bin/env python

import optparse
import logging
import logging_colorer
import sys
from utils import Utils
from load_analysis_lib import LoadAnalysisLib

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

utils = Utils()
#-------------------------------------------------------------------------------
def parse_list_callback(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))

#-------------------------------------------------------------------------------
def setup_parser_options():

    # create parser flag options
    parser = optparse.OptionParser("usage: %prog [option [args]] ")
    parser.add_option("-a", "--analyze", action="store_true", dest="analyze",
            help= \
            "discover a common timestamp threshold amongst all " \
            "data in the output files, " \
            "compute the standard deviations on the data of each output " \
            "file from the timestamp threshold onwards, " \
            "& compute the average of all of the standard deviations")
    parser.add_option('-c', '--clean-up-level', dest="clean_up_level",
            help='Clean up the original data by eliminating ' \
                    '+/- this amount of standard deviations from the mean')
    parser.add_option("-p","--plot", dest="files", type='string',
            action='callback', \
            callback=parse_list_callback, \
            help="plot the std files. i.e. FILES=file1,file2,file3")
    parser.add_option('-l', '--logging-level', dest="logging_level",
            help='Logging level')

    return parser
#-------------------------------------------------------------------------------
def setup_logging(options):

    # set log levels if the user has asked for it
    logging_level = LOGGING_LEVELS.get(options.logging_level)

    if logging_level is None:
        logging_level = 20 # 20 -> 'info' logging level

    logging.basicConfig(level=logging_level,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    utils.set_logging(logging_level)
    LoadAnalysisLib.set_logging(logging_level)

#-------------------------------------------------------------------------------
def main():
    # setup parser options & parse them
    parser = setup_parser_options()
    (options, args) = parser.parse_args()

    # setup logging if requested
    setup_logging(options)

    if not options.analyze and not options.files:
        parser.error("no options given.")
    if len(args) < 1:
        parser.error("no arguments given.")

    if options.analyze:
        # parse and print the original file data provided
        all_file_data = LoadAnalysisLib.parse_output_files(args)
        LoadAnalysisLib.print_file_data("original", all_file_data)

        # clean up outliers if requested & reset all file data to the clean copy
        if options.clean_up_level:
            logging.info("-------------------------------------------------")
            logging.info("Cleaning up outliers in the original data ...")
            clean_up_level = int(options.clean_up_level)

            all_file_data_cleaned = \
                    LoadAnalysisLib.cleanup_file_data(all_file_data, \
                    clean_up_level)
            all_file_data = all_file_data_cleaned

        # discover the a common threshold in all file data, trim file data based
        # off of that threshold, and print the trimmed file data
        all_file_data_trimmed = \
            LoadAnalysisLib.trim_lists_by_common_threshold(all_file_data)
        LoadAnalysisLib.print_file_data("trimmed", all_file_data_trimmed)

        # if no file data errors forced an exit, analyze the trimmed file data
        results = LoadAnalysisLib.analyze(all_file_data_trimmed)
        LoadAnalysisLib.print_results(results)
        
    elif options.files:
        print "plotting..." , options.files

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
