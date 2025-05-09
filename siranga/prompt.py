#!/usr/bin/env python3
"""Prompt Confiuration."""

from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession
import logging

from siranga import ACTIVE_CONNECTIONS, HOSTS
from .nested import NestedCompleter
from .helpers import host_lookup
from .config import  style, field_names

logger = logging.getLogger(__name__)

class Prompt:
    """Custom Prompt Class."""

    def __init__(self, hosts=None):
        self.hosts = hosts
        self.jumps = []
        self.prompt = self.hosts
        self.active_host = None
        self.completer = None
        self._prompt_history = InMemoryHistory()
        self._session = PromptSession(
            history = self._prompt_history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,)

    def get_jumps(self, host):
        """Get host jumps."""
        if host is None:
            return

        if host.ProxyJump:
            jump = host.ProxyJump
            if jump not in self.jumps:
                self.jumps.append(jump)
            self.get_jumps(host_lookup(jump))

    @property
    def prompt(self):
        """Return prompt."""
        return self.__prompt

    @prompt.setter
    def prompt(self, host):
        self.__prompt = []
        self.__prompt.append(('class:username', 'siranga'))

        if host:
            self.get_jumps(host)
            if self.jumps:
                self.__prompt.append(('class:jump', ' ['))
                for jump in self.jumps:
                    self.__prompt.append(('class:jump', f'→{jump}'))
                self.__prompt.append(('class:jump', '→]'))
            self.__prompt.append(('class:host', f' ({host.name})'))
        else:
            self.jumps = []

        self.__prompt.append(('class:arrow', ' → '))
        self.active_host = host

    def show(self):
        """Show Options."""
        if self.active_host:
            self.completer = NestedCompleter({
                '!-D': None,
                '!-L': None,
                '!-R': None,
                '!-KD': None,
                '!-KL': None,
                '!-KR': None,
                '!get': None,
                '!put': PathCompleter(),
                '!shell': None,
                '!addkey': None,
                '!adduser': None,
                '!disconnect': None,
            })
        else:
            _set = {}
            for host in HOSTS:
                _set[host.name] = WordCompleter(field_names)

            base_cmds = {
                '!set': NestedCompleter(_set),
                '!listen': None,
                '!exit': None,
            }

            if ACTIVE_CONNECTIONS:
                base_cmds['!kill'] = WordCompleter([x.name for x in ACTIVE_CONNECTIONS if x]) # noqa
                base_cmds['!active'] = None

            if HOSTS:
                host_names = [x.name for x in HOSTS]
                base_cmds['!connect'] = WordCompleter(host_names)
                base_cmds['!remove'] = WordCompleter(host_names)

            self.completer = NestedCompleter(base_cmds)

        return self._session.prompt(
                self.__prompt,
                completer=self.completer,
                style=style)


