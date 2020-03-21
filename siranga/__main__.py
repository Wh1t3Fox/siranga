#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ssh_config import SSHConfig, Host
from prettytable import PrettyTable
from os.path import expanduser
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

    # lookup host infos
    identity = host_lookup(host)
    ACTIVE_CONNECTION = identity
    ACTIVE_CONNECTIONS.append(identity)

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

    socket_cmd(host, 'exit')
    if os.path.exists(f'{SOCKET_PATH}/{host}'):
        logger.error('Problem killing connection')

    for i, ident in enumerate(ACTIVE_CONNECTIONS):
        if host == host_lookup(host).name:
            del ACTIVE_CONNECTIONS[i]
            break


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

    if not socket_cmd(ACTIVE_CONNECTION.name, 'check'):
        logger.error('No active connection')
        return

    if cmd == '-K':
        socket_cmd(ACTIVE_CONNECTION.name, 'cancel', opts)
    else:
        socket_cmd(ACTIVE_CONNECTION.name, 'forward', f'{cmd} {opts}')


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

        local_path = f'{os.getcwd()}/download/{ACTIVE_CONNECTION.name}{path}'
        if not os.path.exists(local_path):
           os.makedirs(local_path)

        logger.info(f'Downloading to {local_path}')
        command = f'scp -rp -o ControlPath={SOCKET_PATH}/{ACTIVE_CONNECTION.name} {ACTIVE_CONNECTION.name}:{path} {local_path}'

    elif direction == 'put':
        if len(paths) != 2:
            logger.info(transfer_file.__doc__)
            return

        from_path, to_path = paths

        logger.info(f'FROM {from_path} TO {to_path}')
        command = f'scp -rp -o ControlPath={SOCKET_PATH}/{ACTIVE_CONNECTION.name} {from_path} {ACTIVE_CONNECTION.name}:{to_path}'

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

    command = f'stty raw -echo; (echo unset HISTFILE; echo export TERM={os.environ["TERM"]}; echo stty rows {rows} columns {columns}; echo reset; cat) | ssh {SSH_OPTS} {ACTIVE_CONNECTION.name} '
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

def get_active():
    global ACTIVE_CONNECTIONS

    try:
        active_connects = [host_lookup(x) for x in os.listdir(SOCKET_PATH)]
        ACTIVE_CONNECTIONS = list(set(active_connects) & set(ACTIVE_CONNECTIONS))
        logger.info('\n'.join(x.name for x in ACTIVE_CONNECTIONS))
    except FileNotFoundError:
        ACTIVE_CONNECTIONS = []
        return # no active

def set_host(args):
    '''
    Add/Modify ssh_config entry
    Usage:
        Update Field:
            !set <host> <field_name> <value>
        Add Entry:
            !set <host> <hostname> <user> <port>
    '''
    global HOSTS
    config = SSHConfig.load(expanduser(SSH_CONFIG_PATH))
    field_names = ['Host', 'HostName', 'User', 'Port', 'IdentityFile', 'ProxyJump']

    # print out current hosts
    if not args:
        table = PrettyTable()
        table.field_names = field_names
        table.border = False
        table.align = 'l'

        for host in config:
            table.add_row([host.name, host.HostName, host.User, host.Port, host.IdentityFile, host.ProxyJump])
        logger.info(table)
        return

    current_hosts = [host.name for host in config]

    args = list(map(lambda x: x.strip(), args.split()))
    # update entry
    if args[0] in current_hosts and len(args) == 3:
        if args[1] not in field_names:
            logger.error('Use Designated Field Names')
            logger.error(set_host.__doc__)
            return
        config.update(args[0], {args[1]: args[2]})
    # add entry
    elif args[0] not in current_hosts and len(args) == 4:
        new_host = Host(args[0], {
                'HostName': args[1],
                'User': args[2],
                'Port': args[3]
            })
        config.append(new_host)
    # invalid
    else:
        logger.error(set_host.__doc__)
        return

    config.write()
    load_config()

def main():
    global ACTIVE_CONNECTIONS
    global HOSTS

    load_config()

    try:
        for host in os.listdir(SOCKET_PATH):
            ident = host_lookup(host)
            if host == ident.name:
                ACTIVE_CONNECTIONS.append(ident)
    except FileNotFoundError:
        pass


    prompt = Prompt()

    while True:
        try:
            command = prompt.show()
            if not command.startswith('!'):
                if ACTIVE_CONNECTION:
                    try:
                        execute(command, ACTIVE_CONNECTION.name)
                    except Exception as e:
                        logger.error(e)
                else:
                    valid_cmds = '\n\t'.join(prompt.completer.options.keys())
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
                        get_active()
                    elif command == 'kill':
                        kill(args)
                    elif command == 'set':
                        set_host(args)
                    elif command == 'hosts':
                        logger.info('\n'.join([x.name for x in HOSTS]))


        except (KeyboardInterrupt, EOFError) as e:
            pass
        finally:
                prompt.prompt = ACTIVE_CONNECTION


if __name__ == '__main__':
    main()
