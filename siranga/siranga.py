#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import argparse
import logging
import sys
import os

from siranga import ACTIVE_CONNECTION
from siranga.prompt import Prompt
from siranga.helpers import execute

logger = logging.getLogger(__name__)


def connect():
    pass

def interactive_shell():
    # https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
    # Get rows and columns
    orig_tty = subprocess.check_output(b'stty -g'.split())
    tty = subprocess.check_output(b'stty -a'.split()).split(b';')
    rows = int(tty_val[1].split()[-1])
    columns = int(tty_val[2].split()[-1])

    command = f'stty raw -echo; (echo unset HISTFILE;' \
            'echo export TERM={os.environ["TERM"]}; '\
            'echo stty rows {rows} columns {columns}; '\
            'echo reset; cat) | ssh {host} '\
            '"exec python -c \'import pty;pty.spawn(\"/bin/bash\");exit();\'"'
    subprocess.call(command.split(), stderr=subprocess.PIPE)

    subprocess.call(f'stty {orig_tty}'.split())

def main():

    prompt = Prompt()

    while True:
        try:
            command = prompt.show()
            if not command.startswith('!'):
                try:
                    execute(command)
                except FileNotFoundError as e:
                    pass
                continue
            else:
                command = command[1:].split()
                if len(command) > 1:
                    command, args = command[0], ' '.join(command[1:])
                else:
                    command, args = command[0], ''

                # handle special commands
                if command in ['exit', 'quit']:
                    sys.exit(0)

        except (KeyboardInterrupt, EOFError) as e:
            pass
        finally:
                prompt.prompt = ACTIVE_CONNECTION


if __name__ == '__main__':
    main()
