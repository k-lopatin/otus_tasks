# %load log_analyzer.py
#!/usr/bin/env python

from config import Config
from reader import Reader
from log_file_finder import LogFileFinder
from monitoring import log_exceptions
from tests.test_parser import TestParser


@log_exceptions
def main():
    config = Config()
    config.read_config()

    log_file_finder = LogFileFinder(config.log_dir)
    log_file = log_file_finder.get_config_file()

    log_reader = Reader(log_file)
    log_reader.read()


if __name__ == "__main__":
    main()