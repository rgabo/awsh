from __future__ import unicode_literals, print_function

import argparse
import os
from abc import ABCMeta, abstractmethod
from pathlib import PosixPath
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
    commands = []

    def __init__(self, args, context):
        self.args = args
        self.context = context

    def exec(self):
        self.perform(self.args)

    @abstractmethod
    def perform(self, args): pass


class ParsedCommand(Command):
    def exec(self):
        try:
            self.perform(self.parser.parse_args(self.args))
        except ArgumentParserError:
            pass

    @abstractmethod
    def add_arguments(self, parser): pass

    @lazy_property
    def parser(self):
        parser = ArgumentParser(prog=self.name, description=self.description)
        self.add_arguments(parser)
        return parser


def command(name, description=None):
    def decorate(cls):
        cls.name = name
        cls.description = description
        Command.commands.append(cls)
        print('Registered command: {}'.format(name))
    return decorate


@command('cd', description='Change the shell working directory')
class ChangeDirectoryCommand(ParsedCommand):
    def add_arguments(self, parser):
        parser.add_argument('dir', default=os.path.expanduser('~'), nargs='?')

    def perform(self, args):
        os.chdir(args.dir)


@command('echo', description='Write arguments to the standard output')
class EchoCommand(Command):
    def perform(self, args):
        print(' '.join(self.args))


@command('ls', description='List directory contents')
class ListCommand(Command):
    def perform(self, args):
        # fall back to the shell command
        call(['ls'] + self.args)


@command('mount', description='Mount data volumes')
class MountCommand(ParsedCommand):
    def add_arguments(self, parser):
        parser.add_argument('dir', type=PosixPath)

    def perform(self, args):
        self.context.provider(args.dir).mount(args.dir)


@command('pwd', description='Print working directory')
class PrintWorkingDirectoryCommand(Command):
    def perform(self, args):
        print(self.context.cwd)


@command('wc', description='Count the number of words')
class WordCountCommand(ParsedCommand):
    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+')

    def perform(self, args):
        for file in args.file:
            print("{:>8} {}".format(self.get_line_count(file), file))

    def get_line_count(self, name):
        return self.context.sc.textFile(name).count()
