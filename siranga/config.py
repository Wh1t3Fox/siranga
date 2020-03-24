#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit.styles import Style
from os.path import expanduser
import sys

from siranga.nested import NestedCompleter
from siranga import ACTIVE_CONNECTIONS, HOSTS

SSH_CONFIG_PATH = expanduser('~/.ssh/config')
OUTPUT_PATH = expanduser('~/siranga')
SOCKET_PATH = '/tmp/siranga'
field_names = ['Host', 'HostName', 'User', 'Port', 'IdentityFile', 'ProxyJump']

SSH_OPTS = '-o ControlMaster=auto' \
    ' -o Compression=yes' \
    ' -o ForwardX11=yes' \
    ' -o UserKnownHostsFile=/dev/null' \
    ' -o StrictHostKeyChecking=no' \
    ' -o LogLevel=QUIET'

style = Style.from_dict({
    # User input (default text).
    '':          '#c5c8c6',

    # Prompt.
    'username': '#b4b7b4',
    'jump':     '#81a2be',
    'arrow':    '#cc6666',
    'host':     '#b4b7b4',
})

