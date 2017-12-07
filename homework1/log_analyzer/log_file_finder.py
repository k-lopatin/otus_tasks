import os


class LogFileFinder:
    log_dir = None
    date_of_last_analysis = None
    LOG_FILE_STARTSWITH = 'nginx-access-ui.log-'

    def __init__(self, log_dir, date_of_last_analysis):
        if not os.path.exists(log_dir):
            raise IOError('Directory not found')
        self.log_dir = log_dir
        self.date_of_last_analysis = date_of_last_analysis

    def get_config_file(self):
        files = os.listdir(self.log_dir)
        for filename in files:
            full_file_name = os.path.join(self.log_dir, filename)
            if self.is_file_need_to_be_analysed(full_file_name):
                return full_file_name
        return None

    def is_file_need_to_be_analysed(self, filename):
        return self.LOG_FILE_STARTSWITH in filename and self.is_logfile_later_than_last_analysis(filename)

    def is_logfile_later_than_last_analysis(self, filename):
        if self.date_of_last_analysis is None:
            return True
        return float(os.path.getmtime(filename)) > float(self.date_of_last_analysis)
