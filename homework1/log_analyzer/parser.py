from log_info import LogInfo
from log_analyzer_exception import LogAnalyzerException

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
    except LogAnalyzerException:
        return None



