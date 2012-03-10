#!/usr/bin/env python

import optparse

def binary_search(list, max_timestamp):
    return None


def compute(all_lists):
    # Requires that each list in all_lists be sorted 
    # independently in ascending order

    # if no lists provided, return None
    if not all_lists:
        return None
    
    # get total number of lists
    num_lists = len(all_lists)

    # init the max_timestamp lower boundary as the 1st element of the 1st list
    max_timestamp = all_lists[0][0]

    # if only one list is provided, return the first element
    if num_lists == 1:
        min_timestamp = max_timestamp
        return min_timestamp

    # init the list to start the search as the 2nd list
    starting_list = 1

    # find the absolute max timestamp in all of the lists
    absolute_max_timestamp = 0
    for list in all_lists:
        if max(list) > absolute_max_timestamp:
            absolute_max_timestamp = max(list)

    # init the min_timestamp upper boundary as the absolute_max_timestamp
    min_timestamp = absolute_max_timestamp

    # search for the max_timestamp that will exhaust a sorted list.
    # once a list has been exhausted, the last timestamp of this list
    # helps us deduce the min_timestamp that all of the lists share
    # we update both the max & min timestamp until we've reached the end 
    # of all of the lists
    iterations = 0
    while True:
        # if we still have lists to search, continue
        if starting_list < num_lists:
            list = all_lists[starting_list]
            for timestamp in list:
                iterations += 1;
                # if a timestamp is > than the max_timestamp seen so far
                # update it, and move on to next list
                if timestamp > max_timestamp:
                    print "new max_timestamp: " + str(timestamp)
                    max_timestamp = timestamp
                    starting_list += 1
                    break
                # if we reach the end of a list w/o updating the max_timestamp,
                # we store the last timestamp seen in the 
                # list because this is possibly the min_timestamp
                if list.index(timestamp) == (len(list) - 1):
                    print "reached the end of a list " \
                        "w/o finding a max_timestamp - " \
                            "last timestamp seen: " + str(timestamp)

                    # if the timestamp < min_timestamp, update it
                    if timestamp < min_timestamp:
                        min_timestamp = timestamp
                        print "current min_timestamp: " + str(timestamp)
                    # if this is our last list we force an exit of the loop
                    if starting_list == num_lists - 1:
                        starting_list = num_lists + 1
                    # else, if we have more lists to search, continue
                    else:
                        starting_list += 1
        # if we reached the very last list of the 1st run through of the loop
        # start the loop over until we find the final of both the
        # max_timestamp and the min_timestamp
        elif starting_list == num_lists:
            starting_list = 0
        # if we reached a list that doesn't exist, we're done
        elif starting_list > num_lists:
            print "\ntotal iterations: " + str(iterations)
            return min_timestamp
            break;

def parse_list_callback(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))

if __name__ == "__main__":
    parser = optparse.OptionParser("usage: %prog [option [args]] ")
    parser.add_option("-c", "--compute", action="store_true", dest="compute",
            help= \
            "discover a common timestamp threshold amongst all " \
            "local output files, " \
            "compute standard deviations on each output file from " \
            "threshold onwards, " \
            "& compute the average of the standard deviations")
    parser.add_option("-p","--plot", dest="files", type='string', action='callback',
            callback=parse_list_callback, \
            help="plot the std files. i.e. FILES=file1,file2,file3")

    (options, args) = parser.parse_args()

    if not options.compute and not options.files:
        parser.error("no options and/or arguments given.")

    if options.compute:
        print "computing..."

        a = [1,2,3,14,15,26,27,38,49,1000]
        b = [2,3,6,7,8,11,12,14,15,16,25]
        c = [2,3,6,7,8,11,12,14,15,16,288]
        d = [15,16,17,18,22,28,31,32]
        e = [3,14,18,19,20,31,46,51,55,77,132,192,198]

        #all_lists = []
        all_lists = [a,b,c,d,e]

        min_timestamp = compute(all_lists)

        print "\nfinal min_timestamp: " + str(min_timestamp)
    elif options.files:
        print "plotting..." , options.files

