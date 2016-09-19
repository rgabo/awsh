from __future__ import unicode_literals, print_function

import atexit
import os
import sys
import traceback
from pathlib import Path

from awsh.commands import PwdCommand, ShellCommand, CodeCommand, LsCommand
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark.sql import SparkSession


class Context(object):
    def __init__(self):
        self.path = Path(os.getcwd())
        self.spark = self.get_or_create_spark()
        self.sc = self.spark.sparkContext
        atexit.register(lambda: self.sc.stop())

        self.globals = {
            "spark": self.spark,
            "sc": self.sc
        }

    def iterdata(self):
        return self.path.iterdir()

    @property
    def name(self):
        return self.path.name

    @staticmethod
    def get_or_create_spark():
        return SparkSession.builder \
            .appName("awsh") \
            .enableHiveSupport() \
        .getOrCreate()


class Session(object):
    def __init__(self):
        self.context = Context()
        self.history = InMemoryHistory()

    def prompt(self):
        text = prompt(self.get_prompt(), history=self.history)
        if text:
            self.handle_input(text)

    def handle_input(self, input):
        # translate input into command
        if input == 'pwd':
            command = PwdCommand(self.context, input)
        elif input == 'ls':
            command = LsCommand(self.context, input)
        elif input.startswith('!'):
            command = ShellCommand(self.context, input[1:])
        else:
            command = CodeCommand(self.context, input)

        command.perform()

    def get_prompt(self):
        return "{} $ ".format(self.context.name)


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
