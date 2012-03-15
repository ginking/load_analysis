# Company: Sandia National Labs
# Author: Mike Metral
# Email: mdmetra@sandia.gov
# Date: 03/14/12

import sys
import numpy
import logging
import logging_colorer
from utils import Utils
from objects import FileData

class LoadAnalysisLib:
    line_break = "-------------------------------------------------"
    output_to_file = False
#-------------------------------------------------------------------------------
    @staticmethod
    def set_logging(logging_level):
        # Set up the logging configuration and format

        logging.basicConfig(level=logging_level,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
#-------------------------------------------------------------------------------
    @staticmethod
    def parse_data_files(args):
        # Parse & process the data given

        all_file_data = []
        extra_headers_found = False

        # Get the file listing for each directory
        for arg in args:
            dir_listing = Utils.get_dir_listing(arg)
            logging.debug(LoadAnalysisLib.line_break)
            logging.debug("All files found:")
            logging.debug("----------------")
            logging.debug("%s", dir_listing)

            # Process each file in the directory
            for file_entry in dir_listing:
                dirname, filename = file_entry
                file_input = open("%s/%s" % (dirname, filename), "r")

                # Data to collect
                timestamps = []
                deltas = []
                total_headers_found = 0

                # Fix the filepath and make that the file_id
                filepath = Utils.fix_filepath(dirname, filename)
                file_id = filepath

                # Parses the columns of the file input
                for column in file_input:
                    column_data = column.split();
                    try:
                        timestamp = int(column_data[0])
                        delta = int(column_data[1])
                        
                        timestamps.append(timestamp)
                        deltas.append(delta)
                    except:
                        total_headers_found += 1

                # Report if extra headers are found aside from the initial one
                if total_headers_found > 1:
                    extra_headers_found = True
                    logging.error(LoadAnalysisLib.line_break)
                    logging.error("%s extra header(s) found in file: %s" % \
                            (total_headers_found-1, file_id))

                file_data = FileData(file_id, timestamps, deltas)
                all_file_data.append(file_data)

            if extra_headers_found:
                # Exit as there is an error with the data collectected
                #None
                sys.exit(0)

        return all_file_data


#-------------------------------------------------------------------------------
    @staticmethod
    def compute_timestamp_threshold(file_data_list):
        # Computes a timestamp threshold shared amongst the file data, where
        # *Note*: Requires each set of file data in file_data_list to be
        # independently sorted in ascending order

        # Init values to store biggest timestamp
        biggest_timestamp = -1
        biggest_timestamp_file_id = None
        
        logging.info(LoadAnalysisLib.line_break)
        msg = "Computing timestamp threshold amongst file data ..."
        logging.info(msg)

        # Find the biggest timestamp at the head of each list - this will be our
        # threshold
        for file_data in file_data_list:
            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            head_timestamp = timestamps[0]

            logging.debug("")
            logging.debug("viewing head timestamp: " + str(head_timestamp))

            if biggest_timestamp < head_timestamp:
                biggest_timestamp = head_timestamp
                biggest_timestamp_file_id = file_id

            logging.debug("current biggest timestamp: " + \
                    str(biggest_timestamp))
        
        return biggest_timestamp, biggest_timestamp_file_id

#-------------------------------------------------------------------------------
    @staticmethod
    def trim_lists_by_common_threshold(all_file_data):
        # Trims each file's data using a timestamp threshold such that the
        # trimmed data has an equal or greater value relative to the 
        # biggest head out of the file data 

        if not all_file_data:
            return []

        # Compute the timestamp threshold
        threshold, threshold_file_id = \
                LoadAnalysisLib.compute_timestamp_threshold(all_file_data)

        logging.info(LoadAnalysisLib.line_break)
        msg = "Timestamp threshold set at: %s by file: %s" \
                %  (str(threshold), threshold_file_id)
        logging.info(msg)
        if LoadAnalysisLib.output_to_file: Utils.write_to_file("\n\n" + msg)

        debug_iterations = 0

        # Track any empty trimmed file data sets as a result of the threshold
        empty_trimmed_file_data_by_file_data_id = []

        # Iterate through each list & trim out timestamp/delta entries that do
        # not meet the threshold
        for file_data_index, file_data in enumerate(all_file_data):
            debug_iterations += 1
            trimmed_timestamps = []
            trimmed_deltas = []

            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            for timestamp_index, timestamp in enumerate(timestamps):
                debug_iterations += 1
                if timestamp >= threshold:
                    # trim the timestamp & deltas list from this point forward
                    trimmed_timestamps = timestamps[timestamp_index:]
                    trimmed_deltas = deltas[timestamp_index:]
                    break

            # If the trimmed file data is empty track it, else store it
            if len(trimmed_timestamps) == 0 or len(trimmed_deltas) == 0:
                empty_trimmed_file_data_by_file_data_id.append(file_id)
            else:
                file_data.timestamps = trimmed_timestamps
                file_data.deltas = trimmed_deltas
                all_file_data[file_data_index] = file_data

        logging.debug(LoadAnalysisLib.line_break)
        logging.debug("total debug iterations: " + str(debug_iterations))

        # Report any empty lists and quit
        if len(empty_trimmed_file_data_by_file_data_id) > 0:
            logging.error(LoadAnalysisLib.line_break)
            logging.error("Trimming the file data by " + \
                "the timestamp threshold resulted in an empty data set " + \
                "for files: ")

            for file_id in empty_trimmed_file_data_by_file_data_id:
                logging.error("File: " + file_id)
            logging.error("Revise those files, or exclude them to " + \
                    "continue analyzing the data")

            sys.exit(0)

        return all_file_data

#-------------------------------------------------------------------------------
    @staticmethod
    def collect_all_timestamps(file_data_list):
        # Collect the timestamps from each file input

        all_timestamps = []

        for file_data in file_data_list:
            timestamps = file_data.timestamps
            all_timestamps += timestamps

        return all_timestamps
#-------------------------------------------------------------------------------
    @staticmethod
    def collect_all_deltas(file_data_list):
        # Collect the deltas from each file input

        all_deltas = []

        for file_data in file_data_list:
            deltas = file_data.deltas
            all_deltas += deltas

        return all_deltas
#-------------------------------------------------------------------------------
    @staticmethod
    def analyze(file_data_list, dataset_name, log=False):
        # Analyze file data by performing mathematical computations on it

        all_deltas = LoadAnalysisLib.collect_all_deltas(file_data_list)

        # Compute the following for all deltas
        median = numpy.median(all_deltas)
        std = numpy.std(all_deltas)

        if log:
            logging.info(LoadAnalysisLib.line_break)
            msg = "Analysis - (%s) data: median = %s, std = %s" \
                    % (dataset_name, str(median), str(std))
            logging.info(msg)

            if LoadAnalysisLib.output_to_file:
                if dataset_name == "original":
                    Utils.write_to_file("\n" + msg)
                else:
                    Utils.write_to_file("\n\n" + msg)

        return median, std
#-------------------------------------------------------------------------------
    @staticmethod
    def cleanup_file_data(all_file_data, cleanup_level):
        # Clean up the file data by removing any data values that are not +/-
        # the level of stds indicated by cleanup_level

        logging.info(LoadAnalysisLib.line_break)
        msg = "Cleaning up outliers in the data that " + \
                "are not within +/- (%s) standard deviation(s) ..." % \
                str(cleanup_level)
        logging.info(msg)
        if LoadAnalysisLib.output_to_file: Utils.write_to_file("\n\n" + msg)

        # Analyze data & set up cleaning boundaries
        median, std = LoadAnalysisLib.analyze(all_file_data, "original")
        lower_boundary = median - (std * cleanup_level)
        upper_boundary = median + (std * cleanup_level)

        all_file_data_cleaned = []

        # Scrub the file data for values that are not within the cleaning
        # boundaries
        for file_data_index, file_data in enumerate(all_file_data):
            clean_file_data = FileData()
            clean_timestamps = []
            clean_deltas = []

            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            for delta_index, delta in enumerate(deltas):
                if delta >= lower_boundary and delta <= upper_boundary:
                    clean_timestamps.append(timestamps[delta_index])
                    clean_deltas.append(deltas[delta_index])
            
            # If the clean timestamps & deltas are not empty lists, store them
            if clean_timestamps and clean_deltas:
                clean_file_data.file_id = file_id
                clean_file_data.timestamps = clean_timestamps
                clean_file_data.deltas = clean_deltas
                all_file_data_cleaned.append(clean_file_data)

        # If debug set, print clean up logs
        logging_level = \
                logging.getLevelName(logging.getLogger().getEffectiveLevel())
        if logging_level == 'DEBUG':
            for clean_file_data in all_file_data_cleaned:
                timestamps_len = len(clean_file_data.timestamps)
                deltas_len = len(clean_file_data.deltas)

                logging.debug("cleanup-file: " + clean_file_data.file_id + \
                " -- total timestamps: " + str(timestamps_len) + \
                " -- total deltas: " + str(deltas_len))

        return all_file_data_cleaned

#-------------------------------------------------------------------------------
    @staticmethod
    def compute_mean_of_file_data_stds(file_data_list):
        all_stds = []

        # Compute the std of the deltas for each file input & collect it
        for index, file_data in enumerate(file_data_list):
            deltas = file_data.deltas
            std = numpy.std(deltas)

            all_stds.append(std)

        mean_of_all_stds = numpy.mean(all_stds)
        logging.info(LoadAnalysisLib.line_break)
        msg = "Mean of all delta standard deviations found " + \
                "(from all file data): %s" % str(mean_of_all_stds)
        logging.info(msg)
        if LoadAnalysisLib.output_to_file: Utils.write_to_file("\n\n" + msg)
        
#-------------------------------------------------------------------------------
    @staticmethod
    def log_debug_file_data(title, file_data_list):
        # Prints the file data provided

        logging.debug(LoadAnalysisLib.line_break)
        logging.debug(title + " data:")
        logging.debug("---------------")

        for index, file_data in enumerate(file_data_list):
            timestamps_len = len(file_data.timestamps)
            deltas_len = len(file_data.deltas)

            logging.debug("file: " + file_data.file_id + \
            " -- total timestamps: " + str(timestamps_len) + \
            " -- total deltas: " + str(deltas_len))
            
#-------------------------------------------------------------------------------
