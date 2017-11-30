from log_analyzer_exception import LogAnalyzerException


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
            # @todo Change comparison of float to zero.
            if time < 0:
                raise LogAnalyzerException('Incorrect time format: ' + str(time))
            self.time = time
        except ValueError:
            raise LogAnalyzerException('Incorrect time format: ' + str(time))

    def set_api(self, api, stri):
        if len(api) < self.minimum_api_length or api[0] != '/':
            raise LogAnalyzerException('Incorrect api format: ' + str(api) + ' ' + stri)
        self.api = api
