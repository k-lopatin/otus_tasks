import json
import sys
from log_analyzer_exception import LogAnalyzerException


class Config:
    report_size = 1000
    report_dir = "./reports"
    log_dir = "./logs"
    monitoring_dir = './monitoring'

    default_config_filename = 'config.json'
    sys_arg_name_of_config_filename = '--config'

    json_config = {}

    def read_config(self):
        conf_filename = self.get_config_filename()
        try:
            self.json_config = json.load(open(conf_filename))
            self.fill_config()
        except IOError:
            raise LogAnalyzerException('Incorrect config file')

    def get_config_filename(self):
        for arg in sys.argv:
            if arg[0:8] == self.sys_arg_name_of_config_filename:
                return arg[9:]
        return self.default_config_filename

    def fill_config(self):
        if 'REPORTS_SIZE' in self.json_config:
            self.report_size = self.json_config['REPORTS_SIZE']
        if 'REPORT_DIR' in self.json_config:
            self.report_dir = self.json_config['REPORT_DIR']
        if 'LOG_DIR' in self.json_config:
            self.log_dir = self.json_config['LOG_DIR']
        if 'MONITORING_DIR' in self.json_config:
            self.monitoring_dir = self.json_config['MONITORING_DIR']
