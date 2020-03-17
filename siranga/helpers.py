#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

style = Style.from_dict({
    # User input (default text).
    '':          '#c5c8c6',

    # Prompt.
    'username': '#b4b7b4',
    'jump':     '#81a2be',
    'arrow':    '#cc6666',
    'host':     '#b4b7b4',
})

dis_completer = WordCompleter([
    '!connect',
    '!set',
    '!exit',
])

conn_completer = WordCompleter([
    '!disconnect',
    '!get',
    '!put',
    '!-D',
    '!-L',
    '!-R',
    '!-K',
])
