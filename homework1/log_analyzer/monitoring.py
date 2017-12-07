import logging
import os
from log_analyzer_exception import LogAnalyzerException


def set_monitoring_file(monitoring_file):
    if len(monitoring_file) > 0:
        logging.basicConfig(filename=monitoring_file, level=logging.DEBUG)


def log_exceptions(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except LogAnalyzerException as exception:
            logging.error("Error in log analyser: {0}".format(exception))
        except Exception as exception:
            logging.exception("Fatal error: {0}".format(exception))
    return wrapper


def get_ts_file(ts_file_name):
    if not os.path.isfile(ts_file_name):
        return None
    with open(ts_file_name, 'r') as ts_file:
        return ts_file.read()


def write_ts_file(ts_file_name, start_time):
    with open(ts_file_name, 'w') as ts_file:
        ts_file.write(str(start_time))
