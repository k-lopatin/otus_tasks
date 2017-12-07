import os.path
from parser import parse_string
import logging
import gzip


class Reader:
    file_name = None
    statistic = None

    def __init__(self, file_name, statistics):
        if not os.path.isfile(file_name):
            raise IOError('File not found')
        self.file_name = file_name
        self.statistic = statistics

    def read(self):
        count_logs = 0
        log_file = self.open_log_file()
        for log_string in log_file:
            log_info = parse_string(log_string)
            self.statistic.add_api_info(log_info)
            count_logs += 1
        self.log_processed_apis(count_logs)
        log_file.close()

    def open_log_file(self):
        if self.file_name.endswith(".gz"):
            return gzip.open(self.file_name, 'rb')
        else:
            return open(self.file_name)

    def log_processed_apis(self, count_logs):
        unique_apis_number = len(self.statistic.times_by_api)
        logging.info("{0} logs are processed".format(count_logs))
        logging.info("{0} apis are processed".format(unique_apis_number))
