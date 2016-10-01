from __future__ import unicode_literals, print_function

import os
from abc import ABCMeta, abstractmethod
from subprocess import call


class Command(metaclass=ABCMeta):
    def __init__(self, args, context):
        self.args = args
        self.context = context

    @abstractmethod
    def perform(self): pass


class ChangeDirectoryCommand(Command):
    name = 'cd'

    def perform(self):
        if self.args:
            os.chdir(self.args[0])
        else:
            os.chdir(os.path.expanduser('~'))


class EchoCommand(Command):
    name = 'echo'

    def perform(self):
        print(' '.join(self.args))


class ListCommand(Command):
    name = 'ls'

    def perform(self):
        # fall back to the shell command
        call(['ls'] + self.args)


class PrintWorkingDirectoryCommand(Command):
    name = 'pwd'

    def perform(self):
        print(self.context.path)


class WordCountCommand(Command):
    name = 'wc'

    def perform(self):
        if len(self.args) > 1 and self.args[0] == '-l':
            name = self.args[1]
            print("{:>8} {}".format(self.get_line_count(name), name))
        else:
            # fall back to the shell command
            call(['wc'] + self.args)

    def get_line_count(self, name):
        return self.context.sc.textFile(name).count()
