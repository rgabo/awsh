from __future__ import unicode_literals, print_function

import os
from abc import ABCMeta, abstractmethod


class Command(metaclass=ABCMeta):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    @abstractmethod
    def perform(self): pass

    def __str__(self, *args, **kwargs):
        return self.name


class PwdCommand(Command):
    def __init__(self, path):
        super().__init__('pwd', path)

    def perform(self):
        print(self.path)
