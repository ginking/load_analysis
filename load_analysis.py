#!/usr/bin/env python

import optparse


def parse_list_callback(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))

if __name__ == "__main__":
    parser = optparse.OptionParser("usage: %prog " \
            "[-c,-p [file_0,file_1,...file_N]] ")
    parser.add_option("-c", "--compute", action="store_true", dest="compute",
            help="compute a common threshold amongst all output files and " \
            "compute average of standard deviations on them")
    parser.add_option("-p","--plot", type='string', action='callback',
            callback=parse_list_callback, help="plot the std files provided")

    (options, args) = parser.parse_args()

    if not options.compute and not options.plot:
        parser.error("no options and/or arguments given.")

    if options.compute:
        print "computing..."
    elif options.plot:
        print "plotting..." , options.plot

