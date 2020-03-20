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
from siranga.config import SSH_CONFIG_PATH, SSH_OPTS

def load_config():
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        return

    cfg = read_ssh_config(expanduser(SSH_CONFIG_PATH))
    for host in cfg.hosts():
        HOSTS.append(host)

def socket_create(host):
    if not os.path.exists('/tmp/siranga'):
        os.makedirs('/tmp/siranga')

    command = f'ssh -fN {SSH_OPTS} -S /tmp/siranga/{host} {host}'

    try:
        subprocess.call(command.split())
        return True
    except:
        return False


def socket_cmd(request, host, cmd=''):
    # check - that the master process is running
    # forward - request forwardings without command execution
    # cancel - forwardings
    # exit - request the master to exit
    # stop - request the master to stop accepting further multiplexing requests
    command = f'ssh -S /tmp/siranga/{host} -O {request} {cmd} {host}'

    try:
        subprocess.call(command.split())
        return True
    except:
        return False

def execute(cmd, host='', remote=False):
    # Chwck socket 

    if remote:
        cmd = f'ssh {SSH_OPTS} -S /tmp/siranga/{host} {host} {cmd}'
    try:
        output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
        logger.info(output.decode())
    except:
        pass

