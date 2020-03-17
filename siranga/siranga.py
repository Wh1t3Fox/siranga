#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from siranga.prompt import Prompt

logger = logging.getLogger("siranga")

def main():
    
    prompt = Prompt()
    prompt.run()

if __name__ == '__main__':
    main()
