#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import logging
logger = logging.getLogger(__name__)


# check that the master process is running
def socket_check(socket_path):
    command = f'ssh -S {socket_path} -O check -'

    try:
        subprocess.call(command.split())
        return True
    except:
        return False

# request forwardings without command execution
def socket_forward(socket_path, cmd):
    command = f'ssh -S {socket_path} -O forward {cmd} {host}'

# cancel forwardings
def socket_cancel(socket_path, cmd):
    command = f'ssh -S {socket_path} -O cancel {cmd} {host}'

# request the master to exit
def socket_exit(socket_path):
    command = f'ssh -S {socket_path} -O exit {host}'

# request the master to stop accepting further multiplexing requests
def socket_stop(socket_path):
    command = f'ssh -S {socket_path} -O stop -'

def execute(cmd):
    try:
        output = subprocess.check_output(cmd.split())
        logger.info(output.decode())
    except IndexError:
        pass

