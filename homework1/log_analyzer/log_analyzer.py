# %load log_analyzer.py
#!/usr/bin/env python

from config import Config
from reader import Reader
from log_file_finder import LogFileFinder
from monitoring import log_exceptions, write_ts_file, set_monitoring_file
from statistic import Statistic
from template_writer import write_report_to_template
import datetime
from tests.test_parser import TestParser


@log_exceptions
def main():
    # reading config
    config = Config()
    config.read_config()

    set_monitoring_file(config.monitoring_file)

    # looking for the last nginx log to analyze
    log_file_finder = LogFileFinder(config.log_dir)
    log_file = log_file_finder.get_config_file()

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
    if len(config.ts_file) > 0:
        write_ts_file(config.ts_file)


if __name__ == "__main__":
    main()