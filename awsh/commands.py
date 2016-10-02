from __future__ import unicode_literals, print_function

import argparse
import os
from abc import ABCMeta, abstractmethod
from subprocess import call

import sys
from awsh.util import lazy_property


class ArgumentParserError(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        raise ArgumentParserError(message)


class Command(metaclass=ABCMeta):
    def __init__(self, args, context):
        self.args = args
        self.context = context

    def add_arguments(self, parser):
        # collect all arguments into args by default
        parser.add_argument('args', nargs=argparse.REMAINDER)

    def exec(self):
        try:
            self.perform(self.parser.parse_args(self.args))
        except ArgumentParserError:
            pass

    @lazy_property
    def parser(self):
        parser = ArgumentParser(prog=self.name, description=self.description)
        self.add_arguments(parser)
        return parser

    @abstractmethod
    def perform(self, args): pass


class ChangeDirectoryCommand(Command):
    description = 'Change the shell working directory'
    name = 'cd'

    def add_arguments(self, parser):
        parser.add_argument('dir', default=os.path.expanduser('~'), nargs='?')

    def perform(self, args):
        os.chdir(args.dir)


class EchoCommand(Command):
    description = 'Write arguments to the standard output'
    name = 'echo'

    def perform(self, args):
        print(' '.join(args.args))


class ListCommand(Command):
    description = 'List directory contents'
    name = 'ls'

    def perform(self, args):
        # fall back to the shell command
        call(['ls'] + args.args)


class MountCommand(Command):
    description = 'Mount data volumes'
    name = 'mount'

    def perform(self, args):
        pass


class PrintWorkingDirectoryCommand(Command):
    description = 'Print working directory'
    name = 'pwd'

    def perform(self, args):
        print(self.context.path)


class WordCountCommand(Command):
    description = 'Count the number of words'
    name = 'wc'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+')

    def perform(self, args):
        for file in args.file:
            print("{:>8} {}".format(self.get_line_count(file), file))

    def get_line_count(self, name):
        return self.context.sc.textFile(name).count()
