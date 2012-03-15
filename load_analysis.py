#!/usr/bin/env python

# Company: Sandia National Labs
# Author: Mike Metral
# Email: mdmetra@sandia.gov
# Date: 03/14/12

#-------------------------------------------------------------------------------
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
def setup_parser_options():
    # Create parser flag options

    parser = optparse.OptionParser("usage: " + \
            "%prog [options] [data_dir(s)] " + \
            "\n\nDescription:" + \
            "\n------------" + \
            "\n'%prog' processes the file data in the data " + \
            "\ndirector(y/ies) provided & trims the file data so that " + \
            "\nonly data with a common timestamp threshold is " + \
            "\nused in a mathematical analysis." + \
            "\n\nFor help, use %prog -h or %prog --help")
    parser.add_option('-c', '--cleanup-level', dest="cleanup_level",
            help='Clean up the file data by eliminating ' \
                    '+/- this amount of standard deviations from the median')
    parser.add_option("-p","--plot", \
            dest='plot_filename', \
            help="Plot the trimmed file data and save it to the " + \
            "graphs/ directory using the " + \
            "specified filename. Default extension is .png, if none " + \
            "provided. Options to be used with filename: .png, .pdf, .svg")
    parser.add_option("-o","--output-to-file", \
            dest='output_to_file', \
            help="Write output to the results/ directory using the " + \
            "specified filename. *Note: output is done in an appended " + \
            "mode per write, so remove files beforehand, " + \
            "if you plan on reusing the same filename.")
    parser.add_option('-l', '--logging-level', dest="logging_level",
            help="Logging level to use. Default level is set to 'info'. " + \
                "Options (ascendingly inclusive): " + \
                "debug, info, warning, error, critical")

    return parser
#-------------------------------------------------------------------------------
def setup_logging(options):
    # Set log levels if the user has asked for it

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

    # Setup parser options & parse them
    parser = setup_parser_options()
    (options, args) = parser.parse_args()

    # Setup logging if requested
    setup_logging(options)

    # Check for arguments, in this case, directories containing file data
    if len(args) < 1:
        parser.error("no arguments given.")

    # Setup the output file to write the results to, if requested
    if options.output_to_file:
        LoadAnalysisLib.output_to_file = True
        Utils.filepath = 'results/' + options.output_to_file

    # Parse out all of the file data provided
    all_file_data = LoadAnalysisLib.parse_data_files(args)

    # Print debug info about all of the original file data, if requested
    if options.logging_level == 'debug':
        LoadAnalysisLib.log_debug_file_data("original", all_file_data)

    # Analyze all of the original file data and log it
    title, log = "original", True
    LoadAnalysisLib.analyze(all_file_data, title, log)
    
    # Clean up outliers if requested & reset the file data to be the clean data
    if options.cleanup_level:
        cleanup_level = int(options.cleanup_level)

        # Clean the original file data
        all_file_data_cleaned = \
                LoadAnalysisLib.cleanup_file_data(all_file_data, \
                cleanup_level)

        # Reset the original file data to now be the clean file data
        all_file_data = all_file_data_cleaned

        # Analyze all of the clean file data and log it
        title, log = "clean", True
        LoadAnalysisLib.analyze(all_file_data, title, log)

    # Trim the file data (original or clean) based off of a shared timestamp
    # threshold
    all_file_data_trimmed = \
        LoadAnalysisLib.trim_lists_by_common_threshold(all_file_data)

    # Print debug info about the trimmed file data (original or clean),
    # if requested
    if options.logging_level == 'debug':
        LoadAnalysisLib.log_debug_file_data("trimmed", all_file_data_trimmed)

    # Find the mean of all delta standard deviations found (from the trimmed
    # file data)
    LoadAnalysisLib.compute_mean_of_file_data_stds(\
            all_file_data_trimmed)
    
    # Plot the trimmed file data (original or clean)
    if options.plot_filename:
        filepath = '/'.join(['graphs', options.plot_filename])

        # Collect all of the timestamps and deltas
        all_timestamps = \
            LoadAnalysisLib.collect_all_timestamps(all_file_data_trimmed)
        all_deltas = \
            LoadAnalysisLib.collect_all_deltas(all_file_data_trimmed)

        # Plot the data
        plot_title = "Load Analysis"
        Utils.plot_data(all_timestamps, all_deltas, plot_title, filepath)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
