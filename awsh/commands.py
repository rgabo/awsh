from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from codeop import compile_command
from subprocess import call


class Command(metaclass=ABCMeta):
    def __init__(self, session, text):
        self.session = session
        self.text = text

    @abstractmethod
    def perform(self): pass

    def __str__(self, *args, **kwargs):
        return self.text


class CodeCommand(Command):
    globals = {}

    def __init__(self, session, text):
        super().__init__(session, text)

    def perform(self):
        exec(compile_command(self.text), self.globals)


class PwdCommand(Command):
    def __init__(self, session, text):
        super().__init__(session, text)

    def perform(self):
        print(self.session.path)


class ShellCommand(Command):
    def __init__(self, session, text):
        super().__init__(session, text)
        self.command = text[1:]

    def perform(self):
        call(self.command, shell=True)
