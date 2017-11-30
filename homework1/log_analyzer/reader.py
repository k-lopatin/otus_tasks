import os.path
from parser import parse_string
from statistic import Statistic


class Reader:
    file_name = None
    statistic = None

    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            raise IOError('File not found')
        self.file_name = file_name
        self.statistic = Statistic()

    def read(self):
        with open(self.file_name) as log_file:
            for log_string in log_file:
                log_info = parse_string(log_string)
                self.statistic.add_api_info(log_info)
        print(len(self.statistic.times_by_api))

