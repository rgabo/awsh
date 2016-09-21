from __future__ import unicode_literals, print_function

import atexit
import shlex
import sys
import traceback
from codeop import compile_command
from datetime import datetime
from pathlib import Path
from shutil import which

from awsh.commands import *
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark import Row
from pyspark.sql import SparkSession


class Context(object):
    def __init__(self):
        self.spark = self.get_or_create_spark()
        self.sc = self.spark.sparkContext
        atexit.register(lambda: self.sc.stop())

        self.globals = {
            "context": self,
            "spark": self.spark,
            "sc": self.sc
        }

    def sql(self, sql):
        self.frame.registerTempTable("context")
        return self.spark.sql(sql)

    @property
    def name(self):
        return self.path.name

    @property
    def path(self):
        return Path.cwd()

    @property
    def rows(self):
        for child in self.path.iterdir():
            stat = child.stat()
            if child.is_dir():
                type = 'directory'
            else:
                type = 'file'
            yield Row(name=child.name, size=stat.st_size, type=type, modified_at=datetime.fromtimestamp(stat.st_mtime))

    @property
    def frame(self):
        return self.spark.createDataFrame(self.rows)

    @staticmethod
    def get_or_create_spark():
        return SparkSession.builder \
            .appName("awsh") \
            .getOrCreate()


class Session(object):
    def __init__(self):
        self.context = Context()
        self.history = InMemoryHistory()

    def command(self, cmd, args):
        for command in Command.__subclasses__():
            if command.name == cmd:
                return command(args, context=self.context)
        return None

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
        # 2. execute shell command
        elif which(cmd) is not None:
            self.exec_shell(input)
        # 3. execute as code
        else:
            self.exec_code(input)

    def exec_code(self, input):
        exec(compile_command(input), self.context.globals)

    @staticmethod
    def exec_command(command):
        command.perform()

    @staticmethod
    def exec_shell(input):
        call(input, shell=True)

    def exec_sql(self, input):
        self.context.sql(input).show()

    def get_prompt(self):
        return "{} $ ".format(self.context.name)

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
        try:
            session.prompt()
        except (KeyboardInterrupt, EOFError):
            break
        except Exception:
            traceback.print_exc(file=sys.stdout)
            continue
