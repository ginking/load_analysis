class FileData:
    def __init__(self, file_id=None, timestamps=None, deltas=None):
        self.file_id = file_id
        self.timestamps = timestamps
        self.deltas = deltas
class FileAnalysis:
    def __init__(self, file_id, mean, std):
        self.file_id = file_id
        self.mean = mean
        self.std = std
class DataResults:
    def __init__(self, analysis, mean_of_all_stds):
        self.analysis = analysis
        self.mean_of_all_stds = mean_of_all_stds
