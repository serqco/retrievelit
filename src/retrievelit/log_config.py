import logging.config
import os
from datetime import datetime

# create log folder if it doesn't exist
os.makedirs('log', exist_ok=True)

# create new file for each run with dts of start
log_dts = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
filename = f'log/{log_dts}.log'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {
            'format': '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        },
        'simple': {
            'format': '%(asctime)s - [%(levelname)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'logfile': {
            'formatter': 'file',
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': filename,
            'encoding': 'UTF-8',
            'backupCount': 3,
        },
        'console': {
            'formatter': 'simple',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {

    },
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'logfile',
            'console'
        ]
    },
}

logging.config.dictConfig(LOGGING_CONFIG)