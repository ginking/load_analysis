import sys
import numpy
import logging
import logging_colorer
from utils import Utils
from objects import FileData, FileAnalysis, DataResults

class LoadAnalysisLib:
#-------------------------------------------------------------------------------
    utils = Utils()
#-------------------------------------------------------------------------------
    @staticmethod
    def set_logging(logging_level):
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
        biggest_timestamp_file_id = None
        
        # find the biggest timestamp at the head of each list - this will be our
        # threshold for trimming
        logging.debug("-------------------------------------------------")
        logging.debug("Computing timestamp threshold amongst all file data")
        logging.debug("---------------------------------------------------")

        for file_data in all_file_data:
            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            head_timestamp = timestamps[0]

            logging.debug("viewing head timestamp: " + str(head_timestamp))
            if biggest_timestamp < head_timestamp:
                biggest_timestamp = head_timestamp
                biggest_timestamp_file_id = file_id
            logging.debug("current biggest timestamp: " + \
                    str(biggest_timestamp))
            logging.debug("")

        threshold = biggest_timestamp
        logging.info("-------------------------------------------------")
        logging.info("Timestamp threshold set at: %s by file: %s" \
                %  (str(threshold), biggest_timestamp_file_id))

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

        logging.debug("-------------------------------------------------")
        logging.debug("total iterations: " + str(iterations))

        return all_file_data

#-------------------------------------------------------------------------------
    @staticmethod
    def cleanup_file_data(trimmed_file_data, clean_up_level):
        # do cleanup upto removing the +/- level of stds indicated by
        # clean_std_level

        clean_trimmed_file_data = []

        for file_data_index, file_data in enumerate(trimmed_file_data):

            clean_file_data = FileData()
            clean_timestamps = []
            clean_deltas = []

            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            mean = numpy.mean(deltas)
            std = numpy.std(deltas)
            
            lower_boundary = mean - (std * clean_up_level)
            upper_boundary = mean + (std * clean_up_level)

            for delta_index, delta in enumerate(deltas):
                if delta >= lower_boundary and delta <= upper_boundary:
                    clean_timestamps.append(timestamps[delta_index])
                    clean_deltas.append(deltas[delta_index])
            
            if clean_timestamps and clean_deltas:
                clean_file_data.file_id = file_id
                clean_file_data.timestamps = clean_timestamps
                clean_file_data.deltas = clean_deltas
                clean_trimmed_file_data.append(clean_file_data)

        for i, f in enumerate(clean_trimmed_file_data):
            timestamps_len = len(f.timestamps)
            deltas_len = len(f.deltas)

            logging.debug("cleanup-file: " + f.file_id + \
            " -- total timestamps: " + str(timestamps_len) + \
            " -- total deltas: " + str(deltas_len))

        return clean_trimmed_file_data

#-------------------------------------------------------------------------------
    @staticmethod
    def analyze(trimmed_file_data):
        analysis = []

        for index, file_data in enumerate(trimmed_file_data):
            file_id = file_data.file_id
            timestamps = file_data.timestamps
            deltas = file_data.deltas

            mean = numpy.mean(deltas)
            std = numpy.std(deltas)

            new_analysis = FileAnalysis(file_id, mean, std)
            analysis.append(new_analysis)

        temp_all_stds = []
        for index, file_analysis in enumerate(analysis):
            temp_all_stds.append(file_analysis.std)

        mean_of_all_stds = numpy.mean(temp_all_stds)

        results = DataResults(analysis, mean_of_all_stds)
        
        return results

#-------------------------------------------------------------------------------
    @staticmethod
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
    @staticmethod
    def print_results(results):
        analysis = results.analysis
        mean_of_all_stds = results.mean_of_all_stds
        
        logging.debug("-------------------------------------------------")
        logging.debug("Mathematical analysis of trimmed deltas from each file:")
        logging.debug("-----------------------------------------------------")

        for file_analysis in analysis:
            logging.debug("file: " + file_analysis.file_id + \
            " -- mean: " + str(file_analysis.mean) + \
            " -- std: " + str(file_analysis.std))

        logging.info("-------------------------------------------------")
        logging.info("Mean of all standard deviations of the deltas: " + \
               str(mean_of_all_stds))

#-------------------------------------------------------------------------------
