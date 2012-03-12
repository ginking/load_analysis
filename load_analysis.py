#!/usr/bin/env python

import optparse
import logging

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}
#-------------------------------------------------------------------------------
"""
def abs_max(all_lists):
    # find the absolute max timestamp in all of the lists

    absolute_max_timestamp = 0

    for list in all_lists:
        if max(list) > absolute_max_timestamp:
            absolute_max_timestamp = max(list)

    return absolute_max_timestamp
"""
#-------------------------------------------------------------------------------
def parse_output_files():
    a = [(1,2),(2,4),(3,4),(14,4),(15,5),(26,5),(29,7),(49,9)]
    b = [(2,2),(2.5,4),(3,4),(14,4),(15,5),(26,5),(30,7),(49,9)]
    c = [(3,2),(4,4),(3,4),(14,4),(15,5),(26,5),(29,7),(49,9)]
    d = [(5,2),(6,4),(3,4),(14,4),(15,5),(27,5),(29,7),(49,9)]
    e = [(13,2),(77,4),(88,4),(89,4),(99,5),(103,5),(105,7),(192,9)]

    all_lists = [a,b,c,d,e]

    return all_lists

#-------------------------------------------------------------------------------
def trim_lists_by_common_threshold(all_lists):
    # trims each individual list so that they all share timestamps of
    # equal or greater value relative to the biggest head out of all of the
    # original lists (aka the least common threshold of all of the lists)

    # Requires each individual list in all_lists to be sorted in ascending order

    if not all_lists:
        return [None]

    if len(all_lists) == 1:
        return all_lists

    biggest_timestamp = -1

    # find the biggest timestamp at the head of each list - this will be our
    # threshold for trimming
    for current_list in all_lists:
        head = current_list[0]
        timestamp, _ = head
        logging.info("viewing head: " + str(head))
        if biggest_timestamp < timestamp:
            biggest_timestamp = timestamp
        logging.info("current biggest timestamp: " + str(biggest_timestamp))

    threshold = biggest_timestamp
    logging.info("threshold set at: " + str(threshold))

    all_trimmed_lists = []
    iterations = 0

    # iterate through each list and trim out timestamp/output entries that do
    # not meet the threshold
    for current_list in all_lists:
        iterations += 1
        trimmed_list = []
        for entry in current_list:
            timestamp, _ = entry
            iterations += 1
            index = current_list.index(entry)
            if timestamp >= threshold:
                trimmed_list = current_list[index:]
                break
        all_trimmed_lists.append(trimmed_list)

    logging.info("total iterations: " + str(iterations))

    return all_trimmed_lists

#-------------------------------------------------------------------------------
def parse_list_callback(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))

#-------------------------------------------------------------------------------
def main():
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

    (options, args) = parser.parse_args()

    # set log levels if the user has asked for it
    logging_level = LOGGING_LEVELS.get(options.logging_level)
    logging.basicConfig(level=logging_level,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    if not options.compute and not options.files:
        parser.error("no options and/or arguments given.")

    if options.compute:
        all_lists = parse_output_files()

        # discover the a common threshold in all lists and trim the lists based
        # off of that threshold
        trimmed_lists = trim_lists_by_common_threshold(all_lists)

        # show the original & trimmed lists
        logging.info("")
        logging.info("original:")
        for i in all_lists:
            logging.info(i)

        logging.info("")
        logging.info("trimmed:")
        for i in trimmed_lists:
            logging.info(i)

    elif options.files:
        print "plotting..." , options.files

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
