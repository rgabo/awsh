from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from datetime import datetime

from pyspark import Row


class Provider(metaclass=ABCMeta):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def createDataFrame(self, path): pass


class PosixProvider(Provider):
    def createDataFrame(self, path):
        return self.context.spark.createDataFrame(self.get_rows(path))

    @staticmethod
    def get_rows(path):
        for child in path.iterdir():
            stat = child.stat()
            if child.is_dir():
                type = 'directory'
            else:
                type = 'file'
            yield Row(name=child.name, size=stat.st_size, type=type, mtime=datetime.fromtimestamp(stat.st_mtime))
