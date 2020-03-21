#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import argparse
import logging
import sys
import os

from siranga import ACTIVE_CONNECTION, ACTIVE_CONNECTIONS, HOSTS
from siranga.prompt import Prompt
from siranga.config import *
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
    global ACTIVE_CONNECTIONS
    if len(host.split()) != 1:
        logger.error(connect.__doc__)
        return
    del ACTIVE_CONNECTIONS[host]

    socket_cmd(host, 'exit')
    if os.path.exists(f'{SOCKET_PATH}/{host}'):
        logger.error('Problem killing connection')

def port_forward(cmd, opts):
    '''
    Open ports for tunneling
    Usage:
        !-D <port> - setup socks proxy
        !-L <port>:<host>:<port> - local port forward
        !-R <port>:<host>:<port> - Open reverse tunnel
        !-K -[R|L|D]<port>:<host>:<port> - stop forwarding
    '''
    if len(opts.split()) != 1:
        logger.error(port_forward.__doc__)
        return

    if not socket_cmd(ACTIVE_CONNECTION, 'check'):
        logger.error('No active connection')
        return

    if cmd == '-K':
        socket_cmd(ACTIVE_CONNECTION, 'cancel', opts)
    else:
        socket_cmd(ACTIVE_CONNECTION, 'forward', f'{cmd} {opts}')


def transfer_file(direction, args):
    '''
    Recursively transfer file/folder
    Usage:
        !get <remote_path>
        !put <local_path> <remote_path>
    '''

    # specify full paths -- less work ;)
    paths = args.split()
    for path in paths:
        if not path.startswith('/'):
            logger.error('Must specify full path')
            return


    if direction == 'get':
        if len(paths) != 1:
            logger.info(transfer_file.__doc__)
            return

        path = paths[0]

        local_path = f'{os.getcwd()}/download/{ACTIVE_CONNECTION}{path}'
        if not os.path.exists(local_path):
           os.makedirs(local_path)

        logger.info(f'Downloading to {local_path}')
        command = f'scp -rp -o ControlPath={SOCKET_PATH}/{ACTIVE_CONNECTION} {ACTIVE_CONNECTION}:{path} {local_path}'

    elif direction == 'put':
        if len(paths) != 2:
            logger.info(transfer_file.__doc__)
            return

        from_path, to_path = paths

        logger.info(f'FROM {from_path} TO {to_path}')
        command = f'scp -rp -o ControlPath={SOCKET_PATH}/{ACTIVE_CONNECTION} {from_path} {ACTIVE_CONNECTION}:{to_path}'

    try:
       subprocess.call(command, shell=True)
    except Exception as e:
        logger.error(e)

def interactive_shell():
    # https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
    # Get rows and columns
    orig_tty = subprocess.check_output(b'stty -g'.split())
    tty_val = subprocess.check_output(b'stty -a'.split()).split(b';')
    rows = int(tty_val[1].split()[-1])
    columns = int(tty_val[2].split()[-1])

    command = f'stty raw -echo; (echo unset HISTFILE; echo export TERM={os.environ["TERM"]}; echo stty rows {rows} columns {columns}; echo reset; cat) | ssh {SSH_OPTS} {ACTIVE_CONNECTION} '
    # Pre-checks
    # python ?
    if execute('python -V').find(b'command not found') == -1:
        command += '"python -c \'import pty;pty.spawn(\\\"/bin/bash\\\");exit()\'"'
    # python3 ?
    elif execute('python3 -V').find(b'command not found') == -1:
        command += '"python3 -c \'import pty;pty.spawn(\\\"/bin/bash\\\");exit()\'"'
    else:
        # now wut?
        logger.error('TBD')
        return

    subprocess.call(command, shell=True)

    subprocess.call(f'stty {orig_tty.decode()}'.split())

def main():
    global ACTIVE_CONNECTIONS

    load_config()

    try:
        for host in os.listdir(SOCKET_PATH):
            ACTIVE_CONNECTIONS[host] = []
    except FileNotFoundError:
        pass


    prompt = Prompt()

    while True:
        try:
            command = prompt.show()
            if not command.startswith('!'):
                if ACTIVE_CONNECTION:
                    try:
                        execute(command, ACTIVE_CONNECTION)
                    except:
                        pass
                else:
                    valid_cmds = '\n\t'.join(dis_completer.options.keys())
                    logger.error(f'Valid commands are: {chr(10)}{chr(9)}{valid_cmds}')
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
                        port_forward(command, args)
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
