# %load log_analyzer.py
#!/usr/bin/env python

from config import Config
from reader import Reader
import logging
from log_analyzer_exception import LogAnalyzerException
from log_file_finder import LogFileFinder
from monitoring import log_exceptions, write_ts_file, set_monitoring_file, get_ts_file
from statistic import Statistic
from template_writer import write_report_to_template
import datetime
import time
from tests.test_parser import TestParser


@log_exceptions
def main():
    start_time = time.time()

    # reading config
    config = Config()
    config.read_config()

    set_monitoring_file(config.monitoring_file)

    last_monitoring_time = get_ts_file(config.ts_file)

    # looking for the last nginx log to analyze
    log_file_finder = LogFileFinder(config.log_dir, last_monitoring_time)
    log_file = log_file_finder.get_config_file()

    if log_file is None:
        raise LogAnalyzerException('There is no new config files to analyse')

    # parsing of nginx log
    statistic = Statistic(config.report_size)
    log_reader = Reader(log_file, statistic)
    log_reader.read()

    # counting of needed statistics and forming json string with the slowest apis
    json_data = statistic.get_full_json()

    # forming a report html file
    now = datetime.datetime.now()
    report_filename = config.report_dir + '/' + 'report-' + now.strftime("%Y-%m-%d") + '.html'
    write_report_to_template(json_data, 'template.html', report_filename)

    # writing ts-file
    write_ts_file(config.ts_file, start_time)


if __name__ == "__main__":
    main()