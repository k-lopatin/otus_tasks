class Statistic:

    times_by_api = {}
    count_by_api = {}
    time_avg_by_api = {}
    time_med_by_api = {}

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
            self.time_avg_by_api[api] = sum(times) / len(times)
            self.time_med_by_api[api] = sta