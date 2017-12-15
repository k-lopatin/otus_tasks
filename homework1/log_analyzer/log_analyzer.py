# %load log_analyzer.py
#!/usr/bin/env python

import json
import logging
import os
import time
import gzip
import argparse
import re
import collections


LOG_FILE_STARTSWITH = 'nginx-access-ui.log-'


class LogInfo(object):
    api = ''
    time = 0
    minimum_api_length = 3

    def __init__(self, api, time, stri):
        self.set_api(api, stri)
        self.set_time(time)

    def set_time(self, time):
        try:
            time = float(time)
            if time < 0:
                raise StandardError('Incorrect time format: ' + str(time))
            self.time = time
        except ValueError:
            raise StandardError('Incorrect time format: ' + str(time))

    def set_api(self, api, stri):
        if len(api) < self.minimum_api_length or api[0] != '/':
            raise StandardError('Incorrect api format: ' + str(api) + ' ' + stri)
        self.api = api


class Reader(object):
    file_name = None

    logs_count = 0
    incorrect_logs_count = 0

    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            raise IOError('File not found')
        self.file_name = file_name

    def __iter__(self):
        return self.read()

    def read(self):
        log_file = self.open_log_file()
        for log_string in log_file:
            log_string = log_string.decode('utf8')
            self.logs_count += 1
            log_info = parse_string(log_string)
            if log_info is None:
                self.incorrect_logs_count += 1
                continue
            yield log_info
        log_file.close()

    def open_log_file(self):
        if self.file_name.endswith(".gz"):
            return gzip.open(self.file_name, 'rb')
        else:
            return open(self.file_name)


class Statistic(object):

    times_by_api = {}
    count_by_api = {}
    count_percent_by_api = {}
    time_avg_by_api = {}
    time_med_by_api = {}
    time_max_by_api = {}
    time_sum_by_api = {}
    time_percent_by_api = {}

    def add_api_info(self, log_info):
        if log_info is None:
            return
        if log_info.api in self.times_by_api:
            self.times_by_api[log_info.api].append(log_info.time)
        else:
            self.times_by_api[log_info.api] = [log_info.time]

    def count_params(self):
        for api, times in self.times_by_api.items():
            self.count_by_api[api] = len(times)
            times_sum = sum(times)
            self.time_sum_by_api[api] = times_sum
            self.time_avg_by_api[api] = times_sum / len(times)
            self.time_med_by_api[api] = count_median(times)
            self.time_max_by_api[api] = max(times)
        self.count_percent_params()

    def count_percent_params(self):
        sum_count = sum(self.count_by_api.values())
        for api, count in self.count_by_api.iteritems():
            self.count_percent_by_api[api] = (float(count) / float(sum_count)) * 100

        sum_time = sum(self.time_sum_by_api.values())
        for api, count in self.time_sum_by_api.iteritems():
            self.time_percent_by_api[api] = (float(count) / float(sum_time)) * 100


class Analyzer(object):

    def __init__(self, reader, statistic, report_size, incorrect_logs_threshold):
        self.reader = reader
        self.statistic = statistic

        if 0 <= int(incorrect_logs_threshold) <= 100:
            self.incorrect_logs_threshold = int(incorrect_logs_threshold)
        else:
            raise ValueError('Incorrect logs threshold')

        if report_size > 0:
            self.report_size = int(report_size)
        else:
            raise ValueError('Incorrect report size')

    def create_report(self):
        for log_info in self.reader:
            self.statistic.add_api_info(log_info)
        self.statistic.count_params()
        self.log_processed_apis()
        return self.get_full_json()

    def get_full_json(self):
        apis = self.get_longest_apis()
        full_info = []
        for api in apis:
            full_info.append(self.get_info_for_api(api))
        return json.dumps(full_info)

    def get_longest_apis(self):
        sorted_apis = sorted(self.statistic.time_avg_by_api, key=self.statistic.time_avg_by_api.get, reverse=True)
        return sorted_apis[:self.report_size]

    def get_info_for_api(self, api):
        return {
            "count": self.statistic.count_by_api[api],
            "time_avg": self.statistic.time_avg_by_api[api],
            "time_max": self.statistic.time_max_by_api[api],
            "time_sum": self.statistic.time_sum_by_api[api],
            "url": api,
            "time_med": self.statistic.time_med_by_api[api],
            "time_perc": self.statistic.time_percent_by_api[api],
            "count_perc": self.statistic.count_percent_by_api[api]
        }

    def log_processed_apis(self):
        unique_apis_number = len(self.statistic.times_by_api)
        logging.info("{0} logs are processed".format(self.reader.logs_count))
        logging.info("{0} logs are incorrectly parsed".format(self.reader.incorrect_logs_count))
        logging.info("{0} apis are processed".format(unique_apis_number))

    def check_if_too_much_incorrect_logs(self, logs_count, incorrect_logs_count):
        incorrect_percent = round((float(incorrect_logs_count) / float(logs_count)) * 100.0 + 0.5)
        if incorrect_percent > self.incorrect_logs_threshold:
            raise StandardError('Too much incorrect logs that cannot be parsed')


def count_median(numbers_list):
    numbers_list = sorted(numbers_list)
    return numbers_list[len(numbers_list) / 2]


def set_monitoring_file(monitoring_file):
    if len(monitoring_file) > 0:
        logging.basicConfig(filename=monitoring_file, level=logging.DEBUG)


def log_exceptions(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except StandardError as exception:
            logging.exception("Error in log analyser: {0}".format(exception))
        except Exception as exception:
            logging.exception("Fatal error: {0}".format(exception))
        except BaseException as exception:
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


position_of_time_in_log_string = -1
position_of_api_in_log_string = 6


def parse_string(log_str):
    splitted_log_str = log_str.split()
    try:
        log_info = LogInfo(
            api=splitted_log_str[position_of_api_in_log_string],
            time=splitted_log_str[position_of_time_in_log_string],
            stri=log_str
        )
        return log_info
    except StandardError:
        return None


def write_report_to_template(json_data, template_filename, report_filename):
    with open(template_filename, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('$table_json', json_data)

    # Write the file out again
    with open(report_filename, 'w') as report_file:
        report_file.write(filedata)


def read_config_from_file(conf_filename):
    try:
        return json.load(open(conf_filename))
    except IOError:
        raise StandardError('Incorrect config file')


def redefine_config_from_file(config, config_filename):
    if config_filename is False:
        return config
    file_config = read_config_from_file(config_filename)
    config.update(file_config)
    return config


def get_latest_log_file(log_dir):
    if not os.path.exists(log_dir):
        raise IOError('Directory not found')
    files = os.listdir(log_dir)
    latest_filename = None
    latest_date = 0
    for filename in files:
        full_file_name = os.path.join(log_dir, filename)
        if LOG_FILE_STARTSWITH in filename:
            file_date = get_date_of_file(filename)
            if file_date > latest_date:
                latest_filename = full_file_name
                latest_date = file_date
    if latest_date == 0:
        return None
    LatestFile = collections.namedtuple('LatestFilename', ['filename', 'date'])
    return LatestFile(filename=latest_filename, date=latest_date)


def get_date_of_file(filename):
    dates = re.findall(r'\d+', filename)
    if len(dates) > 0:
        return int(dates[0])


def generate_report_filename(report_dir, report_date):
    return report_dir + '/' + 'report-' + str(report_date) + '.html'


def create_report(nginx_log_filename, config):
    statistic = Statistic()
    log_reader = Reader(nginx_log_filename)
    analyser = Analyzer(
        reader=log_reader,
        statistic=statistic,
        report_size=config['REPORT_SIZE'],
        incorrect_logs_threshold=config['INCORRECT_LOGS_THRESHOLD']
    )
    return analyser.create_report()


def get_config_filename_from_command_line_args():
    parser = argparse.ArgumentParser(description='Process config file.')
    parser.add_argument('--config', help='File with configuration params')
    return parser.parse_args().config


def try_redefine_config_from_file(config, default_config_filename):
    try:
        actual_config = get_config_filename_from_command_line_args()
        if actual_config is None:
            actual_config = default_config_filename
        return redefine_config_from_file(config, actual_config)
    except Exception:
        set_monitoring_file(config['MONITORING_FILE'])
        raise Exception('Config file is set incorrectly.')


@log_exceptions
def main():
    start_time = time.time()

    config = {
        'REPORT_SIZE': '1000',
        'REPORT_DIR': './reports',
        'LOG_DIR': './logs',
        'MONITORING_FILE': './monitoring.log',
        'TS_FILE': './log_analyser.ts',
        'INCORRECT_LOGS_THRESHOLD': '10'  # in percent
    }

    default_config_filename = './config.json'

    config = try_redefine_config_from_file(config, default_config_filename)

    set_monitoring_file(config['MONITORING_FILE'])

    latest_log_file = get_latest_log_file(config['LOG_DIR'])
    report_filename = generate_report_filename(config['REPORT_DIR'], latest_log_file.date)

    if latest_log_file.filename is None \
            or os.path.exists(report_filename):
        logging.info('There is no new log files to analyse')
        return

    json_data = create_report(latest_log_file.filename, config)

    write_report_to_template(json_data, 'template.html', report_filename)

    write_ts_file(config['TS_FILE'], start_time)


if __name__ == "__main__":
    main()
