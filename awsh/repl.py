import atexit
import traceback
from codeop import compile_command
from subprocess import call

import sys
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark.sql import SparkSession


def getOrCreateSpark():
    return SparkSession.builder \
                       .appName("awsh") \
                       .enableHiveSupport() \
                       .getOrCreate()


def run():
    print("Initializing Spark")
    spark = getOrCreateSpark()
    sc = spark.sparkContext
    atexit.register(lambda: sc.stop())

    print("""
Welcome to                     __
          ____ __      _______/ /_
         / __ `/ | /| / / ___/ __ \\
        / /_/ /| |/ |/ (__  ) / / /
        \__,_/ |__/|__/____/_/ /_/
""")

    history = InMemoryHistory()

    while True:
        try:
            text = prompt('>>> ', history=history)
            if text:
                handle_input(text)
        except (KeyboardInterrupt, EOFError):
            break
        except Exception:
            traceback.print_exc(file=sys.stdout)
            continue


def exec_code(text):
    exec(compile_command(text))


def exec_shell(text):
    call(text, shell=True)


def handle_input(text):
    # determine what to do with input text
    if text[0] == '!':
        exec_shell(text[1:])
    else:
        exec_code(text)
