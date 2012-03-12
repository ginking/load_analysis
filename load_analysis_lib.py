import logging
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
        all_lists = []

        for arg in args:
            all_files = Utils.get_dir_files(arg)
            logging.debug("All files found: %s", all_files)

        for file_entry in all_files:
            file_data = []

            dirname, filename = file_entry

            file_input = open("%s/%s" % (dirname, filename), "r")

            for column in file_input:
                column_data = column.split();
                try:
                    timestamp = int(column_data[0])
                    delta = int(column_data[1])
                    
                    file_data.append([timestamp, delta])
                except:
                    continue

            file_key = str(dirname + "/" + filename)

            new_file_data = FileData(file_key, file_data)
            all_lists.append(new_file_data)

        return all_lists

#-------------------------------------------------------------------------------
    @staticmethod
    def trim_lists_by_common_threshold(all_lists):
        # trims each individual list so that they all share timestamps of
        # equal or greater value relative to the biggest head out of all of the
        # original lists (aka the least common threshold of all of the lists)

        # Requires each individual list in all_lists to be sorted in ascending order

        if not all_lists:
            return []

        if len(all_lists) == 1:
            return all_lists

        biggest_timestamp = -1

        # find the biggest timestamp at the head of each list - this will be our
        # threshold for trimming
        for current_list in all_lists:
            head = current_list[0]
            timestamp, _ = head
            logging.debug("viewing head: " + str(head))
            if biggest_timestamp < timestamp:
                biggest_timestamp = timestamp
            logging.debug("current biggest timestamp: " + str(biggest_timestamp))

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

        logging.debug("total iterations: " + str(iterations))

        return all_trimmed_lists

#-------------------------------------------------------------------------------
