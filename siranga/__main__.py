#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import argparse
import logging
import sys
import os

from siranga import ACTIVE_CONNECTION, ACTIVE_CONNECTIONS, HOSTS
from siranga.config import SSH_OPTS
from siranga.prompt import Prompt
from siranga.helpers import *

logger = logging.getLogger(__name__)

def connect(host):
    '''
    Connect to the server
    Usage:
        !connect <host>
    '''
    
    global ACTIVE_CONNECTIONS
    global ACTIVE_CONNECTION

    if len(host.split()) != 1:
        logger.error(connect.__doc__)
        return

    # Create SSH connection
    if not socket_create(host):
        return

    # TODO: figure out handling jumps
    ACTIVE_CONNECTION = host
    ACTIVE_CONNECTIONS[host] = []

def disconnect():
    '''
    Disconnect from server
    Usage:
        !disconnect
    '''

    global ACTIVE_CONNECTION
    ACTIVE_CONNECTION = None

def kill(host):
    '''
    Kill the ssh session
    Usage:
        !kill <host>
    '''
    logger.info(f'kill: {host}')
    global ACTIVE_CONNECTIONS
    if len(host.split()) != 1:
        logger.error(connect.__doc__)
        return
    del ACTIVE_CONNECTIONS[host]

    # TODO: Validate socket is gone
    socket_cmd('exit', host)

def port_forward(cmd, opts):
    '''
    Open ports for tunneling
    Usage:
        !-D <port> - setup socks proxy
        !-L <port>:<host>:<port> - local port forward
        !-R <port>:<host>:<port> - Open reverse tunnel
        !-K <port>:<host>:<port> - stop forwarding
    '''
    logger.info(f'port_f: {cmd} {opts}')
    if len(opts.split()) != 1:
        logger.error(port_forward.__doc__)
        return


def transfer_file(direction, args):
    '''
    Recursively transfer file/folder
    Usage:
        !get <remote_path>
        !put <local_path> <remote_path>
    '''
    logger.info(f'transfer: {direction} {args}')
    if len(opts.split()) != 2:
        logger.error(transfer_file.__doc__)
        return

    if cmd == 'get':
        pass
    elif cmd == 'put':
        pass

def interactive_shell():
    # https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
    # Get rows and columns
    orig_tty = subprocess.check_output(b'stty -g'.split())
    tty_val = subprocess.check_output(b'stty -a'.split()).split(b';')
    rows = int(tty_val[1].split()[-1])
    columns = int(tty_val[2].split()[-1])

    command = f'stty raw -echo; (echo unset HISTFILE; echo export TERM={os.environ["TERM"]}; echo stty rows {rows} columns {columns}; echo reset; cat) | ssh {SSH_OPTS} {ACTIVE_CONNECTION} "python -c \'import pty;pty.spawn(\\\"/bin/bash\\\");exit()\'"'

    subprocess.call(command, shell=True)

    subprocess.call(f'stty {orig_tty.decode()}'.split())

def main():

    load_config()

    prompt = Prompt()

    while True:
        try:
            command = prompt.show()
            if not command.startswith('!'):
                if ACTIVE_CONNECTION:
                    remote = True
                else:
                    remote = False
                try:
                    execute(command, ACTIVE_CONNECTION, remote)
                except:
                    pass

                continue
            else:
                command = command[1:].split()
                if len(command) > 1:
                    command, args = command[0], ' '.join(command[1:])
                else:
                    command, args = command[0], ''

                # handle special commands
                if ACTIVE_CONNECTION:
                    if command == 'disconnect':
                        disconnect()
                    elif command == 'shell':
                        interactive_shell()
                    elif command in ['-D', '-K', '-L', '-R']:
                        port_forward(cmd, args)
                    elif command in ['get', 'put']:
                        transfer_file(command, args)
                else:
                    if command in ['exit', 'quit']:
                        sys.exit(0)
                    elif command == 'connect':
                        connect(args)
                    elif command == 'active':
                        logger.info('\n'.join(ACTIVE_CONNECTIONS.keys()))
                    elif command == 'kill':
                        kill(args)
                    elif command == 'hosts':
                        logger.info('\n'.join(CONNECTIONS.keys()))


        except (KeyboardInterrupt, EOFError) as e:
            pass
        finally:
                prompt.prompt = ACTIVE_CONNECTION


if __name__ == '__main__':
    main()
