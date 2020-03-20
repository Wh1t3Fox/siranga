#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession

import logging
logger = logging.getLogger(__name__)

from siranga import ACTIVE_CONNECTIONS
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
            try:
                if len(ACTIVE_CONNECTIONS[host]):
                    self.__prompt.append(('class:jump', '['))
                    for jump in ACTIVE_CONNECTIONS[host]:
                        self.__prompt.append(('class:jumpp', ' → {jump} → '))
                    self.__prompt.append(('class:jump', ']'))
            except KeyError:
                pass
            self.__prompt.append(('class:host', f' ({host})'))

        self.__prompt.append(('class:arrow', ' → '))
        self.active_host = host

    def show(self):
        if self.active_host:
            completer = conn_completer
        else:
            completer = dis_completer

        return self._session.prompt(self.__prompt, completer=completer, style=style)


