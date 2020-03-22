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
        self.completer = None

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
            self.completer = NestedCompleter({
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
            _set = {}
            for host in HOSTS:
                _set[host.name] = WordCompleter(field_names)

            self.completer = NestedCompleter({
                '!connect': WordCompleter([x.name for x in HOSTS]),
                '!hosts': None,
                '!active': None,
                '!set': NestedCompleter(_set),
                '!kill': WordCompleter([x.name for x in ACTIVE_CONNECTIONS]),
                '!exit': None,
            })

        return self._session.prompt(self.__prompt, completer=self.completer, style=style)


