#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession

import logging
logger = logging.getLogger(__name__)

from siranga import ACTIVE_CONNECTION
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

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, hosts):
        self.__prompt = []
        self.__prompt.append(('class:username', 'siranga'))

        if hosts:
            if len(hosts) == 2:
                self.__prompt.append(('class:jump', '['))
                for jump in hosts[1]:
                    self.__prompt.append(('class:jumpp', ' → {jump} → '))
                self.__prompt.append(('class:jump', ']'))
            self.__prompt.append(('class:host', f' ({hosts[0]})'))
            
        else:
            self.completer = dis_completer

        self.__prompt.append(('class:arrow', ' → '))

    def show(self):
        if ACTIVE_CONNECTION:
            completer = conn_completer
        else:
            completer = dis_completer

        return self._session.prompt(self.__prompt, completer=completer, style=style)


