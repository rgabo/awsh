from __future__ import unicode_literals, print_function

import shlex
import sys
import traceback
from codeop import compile_command
from pathlib import Path
from shutil import which

from awsh.commands import *
from awsh.providers import Provider, PosixProvider
from awsh.util import lazy_property
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark.sql import SparkSession


class Context(object):
    def __init__(self):
        self.globals = {
            "context": self,
        }

    def sql(self, sql):
        self.provider(self.cwd).create_df(self.cwd).registerTempTable('cwd')
        return self.spark.sql(sql)

    @property
    def cwd(self):
        return Path.cwd()

    @property
    def sc(self):
        return self.spark.sparkContext

    @lazy_property
    def spark(self):
        return SparkSession.builder \
            .appName("awsh") \
            .getOrCreate()

    def provider(self, path):
        for provider in Provider.providers:
            if str(path).startswith(provider.prefix):
                return provider(self)

        return PosixProvider(self)


class Session(object):
    keyword_commands = ["import"]

    def __init__(self):
        self.context = Context()
        self.history = InMemoryHistory()

    def command(self, cmd, args):
        for command in Command.commands:
            if command.name == cmd:
                return command(args, context=self.context)

    def prompt(self):
        text = prompt(self.get_prompt(), history=self.history)
        if text:
            self.handle_input(text)

    def handle_input(self, input):
        # handle input modifiers
        if input.startswith('>'):
            return self.exec_code(input[1:])
        if input.startswith('!'):
            return self.exec_shell(input[1:])
        if input.startswith('%'):
            return self.exec_sql(input[1:])

        # parse input as single cmd with args
        cmd, *args = self.parse_input(input)
        command = self.command(cmd, args)

        # 1. execute builtin command
        if command:
            self.exec_command(command)
        # 2. execute Python keywords
        elif cmd in self.keyword_commands:
            self.exec_code(input)
        # 3. execute shell command
        elif which(cmd) is not None:
            self.exec_shell(input)
        # 4. execute as code
        else:
            self.exec_code(input)

    def exec_code(self, input):
        exec(compile_command(input), self.context.globals)

    @staticmethod
    def exec_command(command):
        command.exec()

    @staticmethod
    def exec_shell(input):
        call(input, shell=True)

    def exec_sql(self, input):
        self.context.sql(input).show()

    def get_prompt(self):
        return "{} $ ".format(self.context.cwd.name)

    @staticmethod
    def parse_input(input):
        return shlex.split(input, posix=True)


def run():
    session = Session()

    print("""
Welcome to                     __
          ____ __      _______/ /_
         / __ `/ | /| / / ___/ __ \\
        / /_/ /| |/ |/ (__  ) / / /
        \__,_/ |__/|__/____/_/ /_/
""")

    while True:
        # noinspection PyBroadException
        try:
            session.prompt()
        except (KeyboardInterrupt, EOFError):
            break
        except Exception:
            handle_exception(sys.exc_info())


def handle_exception(exc_tuple):
    last_type, last_value, last_traceback = exc_tuple
    print(traceback.format_exception_only(last_type, last_value)[-1].rstrip('\n'))
    sys.last_type = last_type
    sys.last_value = last_value
    sys.last_traceback = last_traceback

if __name__ == '__main__':
    run()
