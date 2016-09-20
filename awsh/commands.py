from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from subprocess import call


class Command(metaclass=ABCMeta):
    def __init__(self, context, args):
        self.context = context
        self.args = args

    @abstractmethod
    def perform(self): pass

    @property
    def sc(self):
        return self.context.sc

    @property
    def spark(self):
        return self.context.spark


class LsCommand(Command):
    def perform(self):
        # fall back to the shell command
        ShellCommand(self.context, ['ls'] + self.args).perform()


class PwdCommand(Command):
    def perform(self):
        print(self.context.path)


class WcCommand(Command):
    def perform(self):
        if self.args and self.args[0] == '-l':
            print("{:>8} {}".format(self.sc.textFile(self.args[1]).count(), self.args[1]))
        else:
            ShellCommand(self.context, ['wc'] + self.args).perform()


class ShellCommand(Command):
    def perform(self):
        call(self.args)


class SqlCommand(Command):
    def perform(self):
        self.context.sql(self.args).show()
