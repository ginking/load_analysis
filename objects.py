# Company: Sandia National Labs
# Author: Mike Metral
# Email: mdmetra@sandia.gov
# Date: 03/14/12

class FileData:
    # Class to store the data from each file input

    def __init__(self, file_id=None, timestamps=None, deltas=None):
        self.file_id = file_id
        self.timestamps = timestamps
        self.deltas = deltas
