import json


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
            self.report_size = report_size

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
            self.time_med_by_api[api] = self.count_median(times)
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

    @staticmethod
    def count_median(numbers_list):
        numbers_list = sorted(numbers_list)
        return numbers_list[len(numbers_list) / 2]