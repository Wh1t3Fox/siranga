#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession

import logging
logger = logging.getLogger(__name__)

from siranga import ACTIVE_CONNECTIONS, HOSTS
from siranga.config import *

class Prompt(object):

    def __init__(self, hosts=None):
        self.hosts = hosts
        self._prompt_history = InMemoryHistory()
        self._session = PromptSession(
            history = self._prompt_history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,)
        self.prompt = self.hosts
        self.active_host = None

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, host):
        self.__prompt = []
        self.__prompt.append(('class:username', 'siranga'))

        if host:
            self.__prompt.append(('class:host', f' ({host.name})'))

        self.__prompt.append(('class:arrow', ' → '))
        self.active_host = host

    def show(self):
        if self.active_host:
            completer = NestedCompleter({
                '!disconnect': None,
                '!get': None,
                '!put': PathCompleter(),
                '!shell': None,
                '!-D': None,
                '!-L': None,
                '!-R': None,
                '!-K': None,
            })
        else:
            inactive = [x.name for x in HOSTS]
            active = [x.name for x in ACTIVE_CONNECTIONS]
            completer = NestedCompleter({
                '!connect': WordCompleter(inactive),
                '!hosts': None,
                '!active': None,
                '!kill': WordCompleter(active),
                '!exit': None,
            })

        return self._session.prompt(self.__prompt, completer=completer, style=style)


