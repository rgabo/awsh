from __future__ import unicode_literals, print_function

import atexit
import os
import sys
import traceback

from awsh.commands import PwdCommand, ShellCommand, CodeCommand
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark.sql import SparkSession


class Path(object):
    def __init__(self, cwd):
        self.cwd = cwd

    def __repr__(self, *args, **kwargs):
        return "Path('{}')".format(self.cwd)

    def __str__(self, *args, **kwargs):
        return self.cwd


class Session(object):
    def __init__(self):
        self.globals = {}
        self.history = InMemoryHistory()
        self.path = Path(os.getcwd())
        self.spark = self.get_or_create_spark_context()
        self.sc = self.spark.sparkContext
        atexit.register(lambda: self.sc.stop())

    def prompt(self):
        text = prompt('>>> ', history=self.history)
        if text:
            self.handle_input(text)

    def handle_input(self, text):
        # translate input into command
        if text == 'pwd':
            command = PwdCommand(self, text)
        elif text.startswith('!'):
            command = ShellCommand(self, text)
        else:
            command = CodeCommand(self, text)

        command.perform()

    @staticmethod
    def get_or_create_spark_context():
        return SparkSession.builder \
            .appName("awsh") \
            .enableHiveSupport() \
            .getOrCreate()


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