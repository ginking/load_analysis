#!/usr/bin/env python

# Company: Sandia National Labs
# Author: Mike Metral
# Email: mdmetra@sandia.gov
# Date: 03/14/12

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
#-------------------------------------------------------------------------------
def parse_list_callback(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))

#-------------------------------------------------------------------------------
def setup_parser_options():

    # create parser flag options
    parser = optparse.OptionParser("usage: %prog [option [args]] ")
    parser.add_option('-c', '--cleanup-level', dest="cleanup_level",
            help='Clean up the original data by eliminating ' \
                    '+/- this amount of standard deviations from the mean')
    parser.add_option("-p","--plot", \
            #action='callback', \
            #callback=parse_list_callback, \
            #help="plot the std files. i.e. FILES=file1,file2,file3")
            dest='plot_filename', \
            #action="store_true", \
            help="plot the trimmed file data and save to the filename " + \
            "provided. Default extension is .png " + \
            "(options are .png, .pdf, .svg)")
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

    Utils.set_logging(logging_level)
    LoadAnalysisLib.set_logging(logging_level)

#-------------------------------------------------------------------------------
def main():
    # setup parser options & parse them
    parser = setup_parser_options()
    (options, args) = parser.parse_args()

    # setup logging if requested
    setup_logging(options)

    if len(args) < 1:
        parser.error("no arguments given.")

    # parse and print the original file data provided
    all_file_data = LoadAnalysisLib.parse_output_files(args)
    LoadAnalysisLib.print_file_data("original", all_file_data)
    LoadAnalysisLib.compute_median_std(all_file_data, "original", True)
    
    # clean up outliers if requested & reset all file data to the clean copy
    if options.cleanup_level:
        cleanup_level = int(options.cleanup_level)

        all_file_data_cleaned = \
                LoadAnalysisLib.cleanup_file_data(all_file_data, \
                cleanup_level)
        all_file_data = all_file_data_cleaned
        LoadAnalysisLib.compute_median_std(all_file_data, "clean", True)

    # discover the a common threshold in all file data, trim file data based
    # off of that threshold, and print the trimmed file data
    all_file_data_trimmed = \
        LoadAnalysisLib.trim_lists_by_common_threshold(all_file_data)
    LoadAnalysisLib.print_file_data("trimmed", all_file_data_trimmed)

    # if no file data errors forced an exit, find the mean of all of the
    # standard deviations computed from each list
    LoadAnalysisLib.compute_mean_of_all_file_data_stds(\
            all_file_data_trimmed)
    
    # Plot output
    if options.plot_filename:
        filepath = '/'.join(['graphs', options.plot_filename])

        all_timestamps, all_deltas = \
                LoadAnalysisLib.prepare_plot_data(all_file_data_trimmed)

        Utils.plot_data(all_timestamps, all_deltas, \
                "Load Analysis", filepath)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
