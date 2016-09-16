from __future__ import unicode_literals, print_function

import atexit

import sys
import traceback

from code import compile_command
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from pyspark.sql import SparkSession


def getOrCreateSpark():
    return SparkSession.builder \
                       .appName("awsh") \
                       .enableHiveSupport() \
                       .getOrCreate()


def main():
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
            source = prompt('>>> ', history=history)
            code = compile_command(source)
            exec(code)
        except (KeyboardInterrupt, EOFError):
            break
        except Exception:
            traceback.print_exc(file=sys.stdout)
            continue

if __name__ == '__main__':
    main()
