#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import argparse
import logging
import sys
import os

from siranga.prompt import Prompt

logger = logging.getLogger("siranga")

def execute_cmd(cmd, *args):
    logger.info(cmd, args)

def transfer_file():
    pass

def interactive_shell(host):
    # https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
    # Get rows and columns

    command = f'stty raw -echo; (echo unset HISTFILE; echo stty rows {rows} columns {columns}; cat) | ssh -T {host} "exec python -c \'import pty;pty.spawn(\"/bin/bash\");exit();\'"'
    subprocess.call(
        command.split(),
        term=os.environ['TERM'],
        shell=True
        )

def main():
    prompt = Prompt()

    while True:
        try:
            command = prompt.show()
            cmd = command[0]
            if not cmd.startswith('!'):
                try:
                    output = subprocess.check_output(command).decode()
                    logger.info(output)
                except FileNotFoundError as e:
                    pass
                continue

            cmd = cmd[1:]
            # ('!cmd', ['args'])
            if len(command) > 1:
                args = command[1:]
            else:
                args = None
        except (KeyboardInterrupt, EOFError) as e:
            pass

        if cmd in ['exit', 'quit']:
            sys.exit(0)

        execute_cmd(cmd, args)

if __name__ == '__main__':
    main()
