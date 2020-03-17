#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.version_info[0] < 3:
    logger.error('This script is supposed to be run with python3.')

