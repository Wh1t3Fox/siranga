#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssh_config
from ssh_config import SSHConfig
from os.path import expanduser
from pathlib import Path
from os import path
import os
import shlex
import subprocess
import logging
logger = logging.getLogger(__name__)

from siranga import HOSTS
from siranga.config import *

def host_lookup(name):
    for ident in HOSTS:
        if name == ident.name:
            return ident
    else:
        return None

def hostname_lookup(ip, user):
    for ident in HOSTS:
        if ip == ident.HostName and user == ident.User:
            return ident
    else:
        return None

def load_config():
    global HOSTS

    del HOSTS[:]
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        if not path.exists(os.path.dirname(SSH_CONFIG_PATH)):
            os.makedirs(os.path.dirname(SSH_CONFIG_PATH))
        Path(SSH_CONFIG_PATH).touch()
        return

    try:
        for host in SSHConfig.load(expanduser(SSH_CONFIG_PATH)):
            HOSTS.append(host)
    except ssh_config.client.EmptySSHConfig:
        pass

def socket_create(host):
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

def execute(cmd, host):
    if host is None:
        return

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

    return output
