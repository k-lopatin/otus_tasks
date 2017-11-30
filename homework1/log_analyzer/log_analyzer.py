# %load log_analyzer.py
#!/usr/bin/env python

from reader import Reader
from log_file_finder import LogFileFinder
from tests.test_parser import TestParser


# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./logs"
}


def main():
    log_dir = config["LOG_DIR"]
    log_file_finder = LogFileFinder(log_dir)
    log_file = log_file_finder.get_config_file()
    log_reader = Reader(log_file)
    log_reader.read()


if __name__ == "__main__":
    main()