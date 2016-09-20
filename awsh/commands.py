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
        # always fall back to the shell command for now
        ShellCommand(self.context, self.text).perform()


class PwdCommand(Command):
    def perform(self):
        print(self.context.path)


class ShellCommand(Command):
    def perform(self):
        call(self.text, shell=True)
