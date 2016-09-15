from __future__ import unicode_literals, print_function

import atexit

from prompt_toolkit import prompt
from pyspark.sql import SparkSession


def getOrCreateSpark():
    return SparkSession.builder.getOrCreate()


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

    while True:
        try:
            text = prompt('>>> ')
            code = compile(text, 'awsh', 'single')
            exec(code)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == '__main__':
    main()
