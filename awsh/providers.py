from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from datetime import datetime

from pyspark import Row


class Provider(metaclass=ABCMeta):
    providers = []

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def create_data_frame(self, path): pass


def provider(name):
    def decorate(cls):
        cls.name = name
        Provider.providers.append(cls)
        print('Registered provider: {}'.format(name))
    return decorate


@provider('posix')
class PosixProvider(Provider):
    def create_data_frame(self, path):
        return self.context.spark.create_data_frame(self.get_rows(path))

    @staticmethod
    def get_rows(path):
        for child in path.iterdir():
            stat = child.stat()
            if child.is_dir():
                type = 'directory'
            else:
                type = 'file'
            yield Row(name=child.name, size=stat.st_size, type=type, mtime=datetime.fromtimestamp(stat.st_mtime))


@provider('buckets')
class S3Provider(Provider):
    def create_data_frame(self, path):
        super(S3Provider, self).create_data_frame(path)
