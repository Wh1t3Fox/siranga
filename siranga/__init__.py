#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.config
import sys
import os


ACTIVE_CONNECTIONS = list()
ACTIVE_CONNECTION = None
HOSTS = list()

from siranga.config import OUTPUT_PATH

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

logger = logging.getLogger(__name__)

if sys.version_info[0] < 3:
    logger.error('This script is supposed to be run with python3.')

