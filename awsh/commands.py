from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from subprocess import call


class Command(metaclass=ABCMeta):
    def __init__(self, context, args):
        self.context = context
        self.args = args

    @abstractmethod
    def perform(self): pass


class LsCommand(Command):
    def perform(self):
        # fall back to the shell command
        ShellCommand(self.context, ['ls'] + self.args).perform()


class PwdCommand(Command):
    def perform(self):
        print(self.context.path)


class ShellCommand(Command):
    def perform(self):
        call(self.args)
