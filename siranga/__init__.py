#!/usr/bin/env python3
"""Init File."""

import logging
import logging.config
import os

from .config import OUTPUT_PATH

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()


ACTIVE_CONNECTIONS = []
ACTIVE_CONNECTION = None
HOSTS = []


if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'screen': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
        'file' :{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'filename': f'{OUTPUT_PATH}/siranga.log'
        }
    },
    'loggers': {
        '': {
            'handlers': ['screen', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})
