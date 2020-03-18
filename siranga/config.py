#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import sys

from siranga.nested import NestedCompleter

style = Style.from_dict({
    # User input (default text).
    '':          '#c5c8c6',

    # Prompt.
    'username': '#b4b7b4',
    'jump':     '#81a2be',
    'arrow':    '#cc6666',
    'host':     '#b4b7b4',
})

dis_completer = NestedCompleter({
    '!connect': WordCompleter([]),
    '!hosts': None,
    '!exit': lambda x: sys.exit(0),
})

conn_completer = NestedCompleter({
    '!disconnect': None,
    '!get': None,
    '!put': None,
    '!shell': None,
    '!-D': None,
    '!-L': None,
    '!-R': None,
    '!-K': None,
})

