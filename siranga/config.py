#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit.styles import Style
import sys

from siranga.nested import NestedCompleter
from siranga import ACTIVE_CONNECTION, ACTIVE_CONNECTIONS, HOSTS

SSH_CONFIG_PATH = '~/.ssh/config'

SSH_OPTS = '-o ControlMaster=auto' \
    ' -o Compression=yes' \
    ' -o ForwardX11=yes' \
    ' -o UserKnownHostsFile=/dev/null' \
    ' -o StrictHostKeyChecking=no' \
    ' -o LogLevel=ERROR'

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
    '!connect': WordCompleter(HOSTS),
    '!active': None,
    '!kill': WordCompleter(ACTIVE_CONNECTIONS.keys()),
    '!exit': None,
})

conn_completer = NestedCompleter({
    '!disconnect': None,
    '!get': None,
    '!put': PathCompleter(),
    '!shell': None,
    '!-D': None,
    '!-L': None,
    '!-R': None,
    '!-K': None,
})

