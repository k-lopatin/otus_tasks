import os

class LogFileFinder:
    log_dir = None

    def __init__(self, log_dir):
        if not os.path.exists(log_dir):
            raise IOError('Directory not found')
        self.log_dir = log_dir

    def get_config_file(self):
        files = os.listdir(self.log_dir)
        return os.path.join(self.log_dir, files[0])
