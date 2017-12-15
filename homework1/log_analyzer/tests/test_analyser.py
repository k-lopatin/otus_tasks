import unittest
from log_analyzer import parse_string, Statistic, LogInfo, Analyzer
import json


class MockReader(object):
    logs_count = 0
    incorrect_logs_count = 0

    def __init__(self, log_infos):
        self.log_infos = log_infos
        self.logs_count = len(log_infos)

    def __iter__(self):
        for log_info in self.log_infos:
            yield log_info



class TestAnalyser(unittest.TestCase):

    def test_parse_log_string(self):
        log_str = '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        log_info = parse_string(log_str)
        self.assertEqual(0.390, log_info.time, 'Time parsed incorrectly')
        self.assertEqual('/api/v2/banner/25019354', log_info.api, 'Api parsed incorrectly')

    def test_statistic(self):
        report_size = 2
        log_info1 = LogInfo('/api1', 10, '')
        log_info2 = LogInfo('/api2', 20, '')
        log_info3 = LogInfo('/api3', 30, '')
        log_info4 = LogInfo('/api1', 60, '')

        statistic = Statistic()
        reader = MockReader([log_info1, log_info2, log_info3, log_info4])
        analyser = Analyzer(reader, statistic, report_size, 10)

        full_json = analyser.create_report()
        full_json_obj = json.loads(full_json)

        self.assertEqual(len(full_json_obj), report_size, 'Report size is incorrect')

        # Check report size
        self.assertEqual(full_json_obj[0]['count'], 2, 'Report size is incorrect')

        # Check api1
        self.assertEqual(full_json_obj[0]['count'], 2, 'Api1 count is incorrect')
        self.assertEqual(full_json_obj[0]['time_avg'], 35, 'Api1 avg is incorrect')
        self.assertEqual(full_json_obj[0]['time_med'], 60, 'Api1 med is incorrect')
        self.assertEqual(full_json_obj[0]['time_sum'], 70, 'Api1 sum is incorrect')
        self.assertEqual(full_json_obj[0]['time_max'], 60, 'Api1 max is incorrect')

        # Check api3
        self.assertEqual(full_json_obj[1]['count'], 1, 'Api3 count is incorrect')
        self.assertEqual(full_json_obj[1]['time_avg'], 30, 'Api3 avg is incorrect')
        self.assertEqual(full_json_obj[1]['time_med'], 30, 'Api3 med is incorrect')
        self.assertEqual(full_json_obj[1]['time_sum'], 30, 'Api3 sum is incorrect')
        self.assertEqual(full_json_obj[1]['time_max'], 30, 'Api3 max is incorrect')
