#!/usr/bin/env python

import optparse
import logging

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}
#-------------------------------------------------------------------------------

def abs_max(all_lists):
    # find the absolute max timestamp in all of the lists

    absolute_max_timestamp = 0

    for list in all_lists:
        if max(list) > absolute_max_timestamp:
            absolute_max_timestamp = max(list)

    return absolute_max_timestamp

#-------------------------------------------------------------------------------

def trim_lists(all_lists):
    # trims each individual list so that they all share timestamps of
    # equal or greater value relative to the biggest head out of all of the
    # original lists (aka the threshold of all of the lists)

    # Requires each individual list in all_lists to be sorted in ascending order

    if not all_lists:
        return [None]

    if len(all_lists) == 1:
        return all_lists

    biggest_head = -1

    # find the biggest head of each list - this will be our threshold for
    # trimming
    for current_list in all_lists:
        head = current_list[0]
        logging.info("viewing head: " + str(head))
        if biggest_head < head:
            biggest_head = head
        logging.info("current biggest head: " + str(biggest_head))

    threshold = biggest_head
    logging.info("threshold set at: " + str(threshold))

    all_trimmed_lists = []
    iterations = 0

    for current_list in all_lists:
        iterations += 1
        trimmed_list = []
        for timestamp in current_list:
            iterations += 1
            index = current_list.index(timestamp)
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

    logging_level = LOGGING_LEVELS.get(options.logging_level)

    logging.basicConfig(level=logging_level,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    if not options.compute and not options.files:
        parser.error("no options and/or arguments given.")

    if options.compute:
        a = [1,2,3,14,15,17,18,19,26,27,28,29,30,38,49,1000]
        b = [2,3,6,7,8,11,12,14,16,23,24,25]
        c = [2.5,3,6,7,8,9,10,11,12,14,15,16,288]
        d = [15,16,17,18,21,22,23,24,25,26,28,31,32,67,881,9991]
        e = [3,14,14.1,14.2,14.3,18,19,51,55,75,76,77,103,105,115,132,192,198]
        f = [4,14,14.11,14.231,14.31,31,46,51,55,67,87,88,89,115,132,192,198]
        g = [55,77,88,89,99,103,105,115,132,192,198]

        all_lists = [a,b,c,d,e,f,g]

        trimmed_lists = trim_lists(all_lists)

        logging.info("")
        for i in all_lists:
            logging.info(i)

        logging.info("")
        for i in trimmed_lists:
            logging.info(i)

    elif options.files:
        print "plotting..." , options.files

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
