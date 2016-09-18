from __future__ import unicode_literals, print_function

import traceback
from codeop import compile_command
from subprocess import call

import atexit
import sys
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark.sql import SparkSession


class Session(object):
    def __init__(self):
        self.history = InMemoryHistory()
        self.spark = self.get_or_create_spark_context()
        self.sc = self.spark.sparkContext
        atexit.register(lambda: self.sc.stop())

    def prompt(self):
        text = prompt('>>> ', history=self.history)
        if text:
            self.handle_input(text)

    def handle_input(self, text):
        # determine what to do with input text
        if text[0] == '!':
            self.exec_shell(text[1:])
        else:
            self.exec_code(text)

    @staticmethod
    def exec_code(text):
        exec(compile_command(text))

    @staticmethod
    def exec_shell(text):
        call(text, shell=True)

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
