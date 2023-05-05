import logging
import datetime


def set_logger():
	logger_init = logging.getLogger('AccessControl')
	file_logger = logging.FileHandler('log/{:%Y-%m-%d %H-%M-%S}.log'.format(datetime.datetime.now()))
	new_format = '[%(asctime)s] - [%(levelname)s] - %(message)s'
	file_logger_format = logging.Formatter(new_format)
	file_logger.setFormatter(file_logger_format)
	logger_init.addHandler(file_logger)
	logger_init.setLevel(logging.DEBUG)
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	console_format = logging.Formatter(new_format)
	console.setFormatter(console_format)
	logging.getLogger('AccessControl').addHandler(console)
	return logger_init
