import sys
import logging
import logging_colorer
from utils import Utils
from objects import FileData

class LoadAnalysisLib:
#-------------------------------------------------------------------------------
    utils = Utils()
#-------------------------------------------------------------------------------
    def set_logging(self, logging_level):
        logging.basicConfig(level=logging_level,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
#-------------------------------------------------------------------------------
    @staticmethod
    def parse_output_files(args):
        all_file_data = []
        extra_headers_found = False

        for arg in args:
            all_files = Utils.get_dir_files(arg)
            logging.debug("-------------------------------------------------")
            logging.debug("All files found:")
            logging.debug("----------------")
            logging.debug("%s", all_files)

        for file_entry in all_files:
            file_data = []

            dirname, filename = file_entry

            file_input = open("%s/%s" % (dirname, filename), "r")
            timestamps = []
            deltas = []

            extra_headers_found_count = -1

            if not dirname.endswith('/'):
                file_id = '/'.join([dirname,filename])
            else:
                file_id = ''.join([dirname,filename])

            for column in file_input:
                column_data = column.split();
                try:
                    timestamp = int(column_data[0])
                    delta = int(column_data[1])
                    
                    timestamps.append(timestamp)
                    deltas.append(delta)
                except:
                    extra_headers_found_count += 1
                    #continue

            if extra_headers_found_count > 0:
                extra_headers_found = True
                logging.error(\
                    "-------------------------------------------------")
                logging.error("%s extra header(s) found in file: %s" % \
                        (extra_headers_found_count, file_id))

            new_file_data = FileData(file_id, timestamps, deltas)
            all_file_data.append(new_file_data)

        if extra_headers_found:
            None
            #sys.exit(0)

        return all_file_data

#-------------------------------------------------------------------------------
    @staticmethod
    def trim_lists_by_common_threshold(all_file_data):
        # trims each individual list so that they all share timestamps of
        # equal or greater value relative to the biggest head out of all of the
        # original lists (aka the least common threshold of all of the lists)

        # Requires each individual list in all_file_data to be sorted in
        # ascending order

        if not all_file_data:
            return []

        biggest_timestamp = -1
        
        # find the biggest timestamp at the head of each list - this will be our
        # threshold for trimming
        logging.debug("-------------------------------------------------")
        logging.debug("Computing threshold")
        logging.debug("-------------------")

        for file_data in all_file_data:
            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            head_timestamp = timestamps[0]

            logging.debug("viewing head timestamp: " + str(head_timestamp))
            if biggest_timestamp < head_timestamp:
                biggest_timestamp = head_timestamp
            logging.debug("current biggest timestamp: " + \
                    str(biggest_timestamp))

        threshold = biggest_timestamp
        logging.info("-------------------------------------------------")
        logging.info("Timestamp threshold set at: " + str(threshold))

        logging.debug("-------------------------------------------------")
        iterations = 0

        # iterate through each list & trim out timestamp/output entries that do
        # not meet the threshold
        for file_data_index, file_data in enumerate(all_file_data):
            iterations += 1
            trimmed_timestamps = []
            trimmed_deltas = []

            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            for timestamp_index, timestamp in enumerate(timestamps):
                iterations += 1
                if timestamp >= threshold:
                    trimmed_timestamps = timestamps[timestamp_index:]
                    trimmed_deltas = deltas[timestamp_index:]
                    break
            file_data.timestamps = trimmed_timestamps
            file_data.deltas = trimmed_deltas
            all_file_data[file_data_index] = file_data

        logging.debug("total iterations: " + str(iterations))

        return all_file_data

#-------------------------------------------------------------------------------
