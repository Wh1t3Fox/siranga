#!/usr/bin/env python3
"""Helper Functions."""

from ssh_config import SSHConfig
from os.path import expanduser
from io import TextIOWrapper
from pathlib import Path
from os import path
import subprocess
import logging
import socket
import shlex
import time
import sys
import os

from siranga import HOSTS, OUTPUT_PATH
from siranga.config import SSH_OPTS, SSH_CONFIG_PATH


logger = logging.getLogger(__name__)

def host_lookup(name):
    """Lookup host."""
    for ident in HOSTS:
        if name == ident.name:
            return ident
    else:
        return None


def hostname_lookup(ip, user):
    """Lookup hostname."""
    for ident in HOSTS:
        if ip == ident.HostName and user == ident.User:
            return ident
    else:
        return None


def load_config():
    """Load configuration file."""
    global HOSTS

    del HOSTS[:]
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        if not path.exists(os.path.dirname(SSH_CONFIG_PATH)):
            os.makedirs(os.path.dirname(SSH_CONFIG_PATH))
        Path(SSH_CONFIG_PATH).touch()
        return

    try:
        for host in SSHConfig(expanduser(SSH_CONFIG_PATH)):
            HOSTS.append(host)
    except Exception:
        pass


def socket_create(host):
    """Create socket."""
    if host is None:
        return

    SOCKET_PATH = f'{OUTPUT_PATH}/{host.HostName}'

    if not os.path.exists(SOCKET_PATH):
        os.makedirs(SOCKET_PATH)

    command = f'ssh -fN {SSH_OPTS} -S {SOCKET_PATH}/control_%r@%h:%p {host.name}'

    try:
        logger.debug(command)
        ret = subprocess.call(shlex.split(command), stderr=subprocess.STDOUT)
        if ret != 0:
            raise Exception("Failed to connect.")
        return True
    except Exception as e:
        logger.error(str(e))
        return False


def socket_cmd(host, request, cmd=''):
    """Send command via -O to SSH socket."""
    if host is None:
        return

    SOCKET_PATH = f'{OUTPUT_PATH}/{host.HostName}/control_%r@%h:%p'

    # check - that the master process is running
    # forward - request forwardings without command execution
    # cancel - forwardings
    # exit - request the master to exit
    # stop - request the master to stop accepting further multiplexing requests
    command = f'ssh -O {request} {cmd} -S {SOCKET_PATH} {host.name}'

    try:
        logger.debug(command)
        subprocess.call(shlex.split(command), stderr=subprocess.STDOUT)
        return True
    except Exception as e:
        logger.debug(str(e))
        return False


def execute(cmd, host) -> bytes:
    """Execute remote command."""
    if host is None:
        return b""

    SOCKET_PATH = f'{OUTPUT_PATH}/{host.HostName}/control_%r@%h:%p'

    # Chwck socket
    output = b''
    command = f'ssh {SSH_OPTS} -S {SOCKET_PATH} {host.name} {shlex.quote(cmd)}'

    try:
        logger.debug(command)
        out = subprocess.check_output(command, shell=True)
        logger.info(out.decode())

        output = out
    except Exception as e:
        logger.debug(str(e))
        output = str(e).encode()

    if not output:
        return b""

    return output


def recv_timeout(sock):
    """Recv data."""
    sock.setblocking(0)
    recv_data = b''
    buf = b''
    begin = time.time()

    while True:
        # wait a sec
        if recv_data and time.time() - begin > 1:
            break
        # there's no data, so wait 2s
        elif time.time() - begin > 2:
            break
        try:
            buf = sock.recv(1024)
            if buf:
                recv_data += buf
                begin = time.time()
            else:
                time.sleep(0.1)
        except socket.error as e: # noqa
            if not e.errno == 11:
                raise
    return recv_data


def listener_handler(conn):
    """Create Listener."""
    # Unbuffered stdin
    sys.stdin = TextIOWrapper(
            os.fdopen(sys.stdin.fileno(), 'br', buffering = 0),
            write_through = True,
            line_buffering = False
    )

    sys.stdout.buffer.write(recv_timeout(conn))
    sys.stdout.flush()
    orig_tty = None
    while True:
        send_data = sys.stdin.buffer.read(64)
        if send_data:
            if send_data == b'!pty\n':
                orig_tty = subprocess.check_output(shlex.split('stty -g'))
                tty_val = subprocess.check_output(shlex.split('stty -a')).split(b';')
                rows = int(tty_val[1].split()[-1])
                columns = int(tty_val[2].split()[-1])
                send_data = (
                    "(echo unset HISTFILE; echo export HISTCONTROL=ignorespace; echo tput rmam; " # noqa
                    f"echo export TERM={os.environ['TERM']}; "
                    f"echo stty rows {rows} columns {columns}; "
                    "echo reset; cat) | python -c 'import pty; pty.spawn(\"/bin/bash\")'\n".encode() # noqa
                )
                subprocess.call(shlex.split('stty raw -echo'), shell=True)
            conn.sendall(send_data)
            if send_data == b'exit\n':
                break
        else:
            continue
        sys.stdout.buffer.write(recv_timeout(conn))
        sys.stdout.flush()
    conn.close()
    if orig_tty:
        subprocess.check_output(shlex.split(f'stty {orig_tty.decode()}'))

