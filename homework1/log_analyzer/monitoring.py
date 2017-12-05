import logging
from log_analyzer_exception import LogAnalyzerException


def log_exceptions(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except LogAnalyzerException as exception:
            logging.error("Error in log analyser: {0}".format(exception))
        except Exception as exception:
            logging.exception("Fatal error: {0}".format(exception))
    return wrapper
