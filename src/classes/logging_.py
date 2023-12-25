import datetime
import logging


class Logging:
    @staticmethod
    def log_error(error):
        try:
            date = datetime.datetime.now()
            log_text = f'{date}    {error}\n'
            logging.warning(log_text)
        except Exception as ex:
            return f'Unable to write error log: {ex}'

