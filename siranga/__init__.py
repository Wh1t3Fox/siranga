#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging 
import logging.config
import sys

ACTIVE_CONNECTIONS = dict()
ACTIVE_CONNECTION = None
HOSTS = list()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})

logger = logging.getLogger(__name__)

if sys.version_info[0] < 3:
    logger.error('This script is supposed to be run with python3.')

