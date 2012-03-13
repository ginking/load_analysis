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
load_analysis_lib = LoadAnalysisLib()
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
    load_analysis_lib.set_logging(logging_level)

#-------------------------------------------------------------------------------
def print_file_data(title, file_data_list):
    # Prints the file data provided

    # only for when printing the trimmed data
    empty_trimmed_file_data_by_file_data_id = []

    logging.debug("-------------------------------------------------")
    logging.debug(title + " data:")
    logging.debug("---------------")
    for index, file_data in enumerate(file_data_list):
        timestamps_len = len(file_data.timestamps)
        deltas_len = len(file_data.deltas)

        logging.debug("file: " + file_data.file_id + \
        " -- total timestamps: " + str(timestamps_len) + \
        " -- total deltas: " + str(deltas_len))
        
        if title == "trimmed":
            if timestamps_len == 0 or deltas_len == 0:
                empty_trimmed_file_data_by_file_data_id.append(\
                    file_data.file_id)

    # Report any empty lists and quit
    if title == "trimmed":
        if len(empty_trimmed_file_data_by_file_data_id) > 0:
            logging.error("-------------------------------------------------")
            logging.error("Trimming the original file data by " + \
                "the timestamp threshold resulted in an empty data set " + \
                "for files: ")
            for file_id in empty_trimmed_file_data_by_file_data_id:
                logging.error("File: " + file_id)
            sys.exit(0)

#-------------------------------------------------------------------------------
def print_results(results):
    analysis = results.analysis
    mean_of_all_stds = results.mean_of_all_stds
    
    logging.debug("-------------------------------------------------")
    logging.debug("Standard deviations of trimmed deltas from each file:")
    logging.debug("-----------------------------------------------------")

    for file_analysis in analysis:
        logging.debug("file: " + file_analysis.file_id + \
        " -- mean: " + str(file_analysis.mean) + \
        " -- std: " + str(file_analysis.std))

    logging.info("-------------------------------------------------")
    logging.info("Mean of all standard deviations of the deltas:")
    logging.info("----------------------------------------------")
    logging.info(str(mean_of_all_stds))
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
        all_file_data = load_analysis_lib.parse_output_files(args)
        print_file_data("original", all_file_data)

        # clean up any outliers first
        if options.clean_up_level:
            logging.info("-------------------------------------------------")
            logging.info("Cleaning up outliers in the original data ...")
            clean_up_level = int(options.clean_up_level)

            clean_trimmed_file_data = \
                    load_analysis_lib.cleanup_file_data(all_file_data, \
                    clean_up_level)
            all_file_data = clean_trimmed_file_data

        # discover the a common threshold in all file data, trim them based
        # off of that threshold, and print the trimmed file data
        trimmed_file_data = \
            load_analysis_lib.trim_lists_by_common_threshold(all_file_data)
        print_file_data("trimmed", all_file_data)

        # if no file data errors have force an exit, analyze the trimmed file
        # data
        results = load_analysis_lib.analyze(trimmed_file_data)
        print_results(results)
        

    elif options.files:
        print "plotting..." , options.files


#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
