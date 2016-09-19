from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from codeop import compile_command
from subprocess import call


class Command(metaclass=ABCMeta):
    def __init__(self, context, text):
        self.context = context
        self.text = text

    @abstractmethod
    def perform(self): pass

    def __str__(self, *args, **kwargs):
        return self.text


class CodeCommand(Command):
    def perform(self):
        exec(compile_command(self.text), self.context.globals)


class LsCommand(Command):
    def perform(self):
        for row in self.context.iterdata():
            print(row.name)


class PwdCommand(Command):
    def perform(self):
        print(self.context.path)


class ShellCommand(Command):
    def perform(self):
        call(self.text, shell=True)
