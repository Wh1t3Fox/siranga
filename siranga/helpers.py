#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ssh_config import SSHConfig
from os.path import expanduser
from os import path
import os
import subprocess
import logging
logger = logging.getLogger(__name__)

from siranga import HOSTS
from siranga.config import *

def host_lookup(name):
    for ident in HOSTS:
        if name == ident.name:
            return ident

def load_config():
    del HOSTS[:]
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        return

    for host in SSHConfig.load(expanduser(SSH_CONFIG_PATH)):
        HOSTS.append(host)

def socket_create(host):
    if not os.path.exists(SOCKET_PATH):
        os.makedirs(SOCKET_PATH)

    command = f'ssh -fN {SSH_OPTS} -S {SOCKET_PATH}/{host} {host}'

    try:
        logger.debug(command)
        subprocess.call(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False


def socket_cmd(host, request, cmd=''):
    # check - that the master process is running
    # forward - request forwardings without command execution
    # cancel - forwardings
    # exit - request the master to exit
    # stop - request the master to stop accepting further multiplexing requests
    command = f'ssh -O {request} {cmd} -S {SOCKET_PATH}/{host} {host}'

    try:
        logger.debug(command)
        subprocess.call(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        return False

def execute(cmd, host=''):
    # Chwck socket

    command = f'ssh {SSH_OPTS} -S {SOCKET_PATH}/{host} {host} {cmd}'

    try:
        logger.debug(command)
        output = subprocess.check_output(command.split(), stderr=subprocess.STDOUT)
        logger.info(output.decode())
        return output
    except Exception as e:
        logger.error(f'{cmd: {str(e)}}')
