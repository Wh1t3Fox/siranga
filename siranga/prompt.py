#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

class Prompt(object):

    def __init__(self, hosts=None):

        self.hosts = hosts


    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, hosts):
        text = 'siranga' 

        if hosts:
            if len(hosts) == 2:
                if hosts[1]:
                    boxes = ' → '.join(hosts[1])
                    text += f'[ {boxes} ]'
            text += f' [ {hosts[0]} ]'

        self.__prompt = f'{text} → '


    def run(self):
        while True:
            self.prompt = self.hosts
            inpt = prompt(self.__prompt)
