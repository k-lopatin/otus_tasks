# %load log_analyzer.py
#!/usr/bin/env python

import json
import logging
import os
import time
import gzip
import argparse
import re


LOG_FILE_STARTSWITH = 'nginx-access-ui.log-'


class LogInfo:
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


class Reader:
    file_name = None
    statistic = None
    incorrect_logs_threshold = 10

    def __init__(self, file_name, statistics, incorrect_logs_threshold):
        if not os.path.isfile(file_name):
            raise IOError('File not found')
        self.file_name = file_name
        self.statistic = statistics
        self.incorrect_logs_threshold = incorrect_logs_threshold

    def read(self):
        logs_count = 0
        incorrect_logs_count = 0
        log_file = self.open_log_file()
        for log_string in log_file:
            log_string = log_string.decode('utf8')
            logs_count += 1
            log_info = parse_string(log_string)
            if log_info is None:
                incorrect_logs_count += 1
                continue
            self.statistic.add_api_info(log_info)
        log_file.close()
        self.log_processed_apis(logs_count, incorrect_logs_count)
        self.check_if_too_much_incorrect_logs(logs_count, incorrect_logs_count)

    def open_log_file(self):
        if self.file_name.endswith(".gz"):
            return gzip.open(self.file_name, 'rb')
        else:
            return open(self.file_name)

    def log_processed_apis(self, logs_count, incorrect_logs_count):
        unique_apis_number = len(self.statistic.times_by_api)
        logging.info("{0} logs are processed".format(logs_count))
        logging.info("{0} logs are incorrectly parsed".format(incorrect_logs_count))
        logging.info("{0} apis are processed".format(unique_apis_number))

    def check_if_too_much_incorrect_logs(self, logs_count, incorrect_logs_count):
        incorrect_percent = round((float(incorrect_logs_count) / float(logs_count)) * 100.0 + 0.5)
        if incorrect_percent > self.incorrect_logs_threshold:
            raise StandardError('Too much incorrect logs that cannot be parsed')


class Statistic:

    report_size = 1000

    times_by_api = {}
    count_by_api = {}
    count_percent_by_api = {}
    time_avg_by_api = {}
    time_med_by_api = {}
    time_max_by_api = {}
    time_sum_by_api = {}
    time_percent_by_api = {}

    def __init__(self, report_size):
        if report_size > 0:
            self.report_size = int(report_size)

    def add_api_info(self, log_info):
        if log_info is None:
            return
        if log_info.api in self.times_by_api:
            self.times_by_api[log_info.api].append(log_info.time)
        else:
            self.times_by_api[log_info.api] = [log_info.time]

    def get_full_json(self):
        self.count_params()
        apis = self.get_longest_apis()
        full_info = []
        for api in apis:
            full_info.append(self.get_info_for_api(api))
        return json.dumps(full_info)

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

    def get_longest_apis(self):
        sorted_apis = sorted(self.time_avg_by_api, key=self.time_avg_by_api.get, reverse=True)
        return sorted_apis[0:self.report_size]

    def get_info_for_api(self, api):
        return {
            "count": self.count_by_api[api],
            "time_avg": self.time_avg_by_api[api],
            "time_max": self.time_max_by_api[api],
            "time_sum": self.time_sum_by_api[api],
            "url": api,
            "time_med": self.time_med_by_api[api],
            "time_perc": self.time_percent_by_api[api],
            "count_perc": self.count_percent_by_api[api]
        }


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
    return latest_filename, latest_date


def get_date_of_file(filename):
    dates = re.findall(r'\d+', filename)
    if len(dates) > 0:
        return int(dates[0])


def check_if_report_exist(report_dir, log_date):
    if not os.path.exists(report_dir):
        return False
    files = os.listdir(report_dir)
    for filename in files:
        file_date = get_date_of_file(filename)
        if file_date == log_date:
            return True
    return False


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

    # Reading config filename from command line arguments
    parser = argparse.ArgumentParser(description='Process config file.')
    parser.add_argument('--config', help='File with configuration params')
    config_filename = parser.parse_args().config

    # redefining parameters of config from config file
    try:
        if config_filename is not None:
            config = redefine_config_from_file(config, config_filename)
    except Exception:
        set_monitoring_file(config['MONITORING_FILE'])
        logging.exception('Config file is set incorrectly.')
        return

    set_monitoring_file(config['MONITORING_FILE'])

    # looking for the last nginx log to analyze
    log_file, log_file_date = get_latest_log_file(config['LOG_DIR'])
    if log_file is None or check_if_report_exist(config['REPORT_DIR'], log_file_date):
        raise StandardError('There is no new log files to analyse')

    # parsing of nginx log
    statistic = Statistic(config['REPORT_SIZE'])
    log_reader = Reader(log_file, statistic, config['INCORRECT_LOGS_THRESHOLD'])
    log_reader.read()

    # counting of needed statistics and forming json string with the slowest apis
    json_data = statistic.get_full_json()

    # forming a report html file
    report_filename = config['REPORT_DIR'] + '/' + 'report-' + str(log_file_date) + '.html'
    write_report_to_template(json_data, 'template.html', report_filename)

    # writing ts-file
    write_ts_file(config['TS_FILE'], start_time)


if __name__ == "__main__":
    main()
