#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sshconf import read_ssh_config, empty_ssh_config
from os.path import expanduser
from os import path
import os
import subprocess
import logging
logger = logging.getLogger(__name__)

from siranga import HOSTS
from siranga.config import *

def load_config():
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        return

    cfg = read_ssh_config(expanduser(SSH_CONFIG_PATH))
    for host in cfg.hosts():
        HOSTS.append(host)

def socket_create(host):
    if not os.path.exists(SOCKET_PATH):
        os.makedirs(SOCKET_PATH)

    command = f'ssh -fN {SSH_OPTS} -S {SOCKET_PATH}/{host} {host}'

    try:
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
        subprocess.call(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        return False

def execute(cmd, host=''):
    # Chwck socket

    cmd = f'ssh {SSH_OPTS} -S {SOCKET_PATH}/{host} {host} {cmd}'

    try:
        output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
        logger.info(output.decode())
        return output
    except:
        pass
