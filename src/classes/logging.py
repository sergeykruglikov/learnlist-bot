import datetime


class Logging:
    @staticmethod
    def log_error(error):
        log_file_path = '/var/log/learnlist.err.log'
        date = datetime.datetime.now()
        try:
            with open(log_file_path, 'a+', encoding='utf-8') as f:
                f.write(f'{date}    {error}\n')
        except Exception as ex:
            return f'Unable to write error log: {ex}'
