#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession

from siranga.helpers import *

class Prompt(object):

    def __init__(self, hosts=None):
        self.hosts = hosts
        self._prompt_history = InMemoryHistory()
        self._session = PromptSession(
            history = self._prompt_history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,)

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, hosts):
        self.__prompt = []
        self.__prompt.append(('class:username', 'siranga'))

        if hosts:
            self.completer = conn_completer
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
        self.prompt = self.hosts
        return self._session.prompt(self.__prompt, completer=self.completer, style=style).split()


