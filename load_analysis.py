#!/usr/bin/env python

import optparse
import logging
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
    parser.add_option("-c", "--compute", action="store_true", dest="compute",
            help= \
            "discover a common timestamp threshold amongst all " \
            "local output files, " \
            "compute standard deviations on each output file from " \
            "threshold onwards, " \
            "& compute the average of the standard deviations")
    parser.add_option("-p","--plot", dest="files", type='string',
            action='callback', \
            callback=parse_list_callback, \
            help="plot the std files. i.e. FILES=file1,file2,file3")
    parser.add_option('-l', '--logging-level', help='Logging level')

    return parser
#-------------------------------------------------------------------------------
def setup_logging(options):

    # set log levels if the user has asked for it
    logging_level = LOGGING_LEVELS.get(options.logging_level)
    logging.basicConfig(level=logging_level,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    utils.set_logging(logging_level)
    load_analysis_lib.set_logging(logging_level)

#-------------------------------------------------------------------------------

def main():
    parser = setup_parser_options()

    (options, args) = parser.parse_args()

    setup_logging(options)

    if not options.compute and not options.files:
        parser.error("no options given.")
    if len(args) < 1:
        parser.error("no arguments given.")

    if options.compute:
        all_lists = load_analysis_lib.parse_output_files(args)

        # discover the a common threshold in all lists and trim the lists based
        # off of that threshold
        trimmed_lists = \
            load_analysis_lib.trim_lists_by_common_threshold(all_lists)

        # show the original & trimmed lists
        logging.info("original lists:")
        for i in all_lists:
            logging.info(i)

        logging.info("trimmed lists:")
        for i in trimmed_lists:
            logging.info(i)

    elif options.files:
        print "plotting..." , options.files

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
