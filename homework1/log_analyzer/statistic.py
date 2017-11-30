class Statistic:

    times_by_api = {}

    def add_api_info(self, log_info):
        if log_info is None:
            return
        if log_info.api in self.times_by_api:
            self.times_by_api[log_info.api].append(log_info.time)
        else:
            self.times_by_api[log_info.api] = [log_info.time]

