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


class Session(object):
    def __init__(self):
        self.globals = {}
        self.history = InMemoryHistory()
        self.path = Path(os.getcwd())
        self.spark = self.get_or_create_spark_context()
        self.sc = self.spark.sparkContext
        atexit.register(lambda: self.sc.stop())

    def prompt(self):
        text = prompt(self.get_prompt(), history=self.history)
        if text:
            self.handle_input(text)

    def handle_input(self, input):
        # translate input into command
        if input == 'pwd':
            command = PwdCommand(self, input)
        elif input == 'ls':
            command = LsCommand(self, input)
        elif input.startswith('!'):
            command = ShellCommand(self, input)
        else:
            command = CodeCommand(self, input)

        command.perform()

    def get_prompt(self):
        return "{} $ ".format(self.path.name)

    def iterdata(self):
        return self.path.iterdir()

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
