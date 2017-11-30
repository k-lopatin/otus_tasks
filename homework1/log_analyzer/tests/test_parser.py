import unittest
from parser import parse_string


class TestParser(unittest.TestCase):

    def test_parse_log_string(self):
        log_str = '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        log_info = parse_string(log_str)
        self.assertEqual(0.390, log_info.time, 'Time parsed incorrectly')
        self.assertEqual('/api/v2/banner/25019354', log_info.api, 'Api parsed incorrectly')
