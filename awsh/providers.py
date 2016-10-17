from __future__ import unicode_literals, print_function

from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import PurePath, PosixPath
from subprocess import run

from pyspark import Row


class Provider(metaclass=ABCMeta):
    providers = []

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def create_df(self, path): pass

    @abstractmethod
    def mount(self, path): pass


def provider(name, prefix):
    def decorate(cls):
        cls.name = name
        cls.prefix = prefix
        Provider.providers.append(cls)
        print('Registered provider: {}'.format(name))
    return decorate


class PosixProvider(Provider):
    def create_df(self, path):
        return self.context.spark.create_df(self.get_rows(path))

    @staticmethod
    def get_rows(path):
        for child in path.iterdir():
            stat = child.stat()
            if child.is_dir():
                type = 'directory'
            else:
                type = 'file'
            yield Row(name=child.name, size=stat.st_size, type=type, mtime=datetime.fromtimestamp(stat.st_mtime))

    def mount(self, path):
        raise NotImplementedError('Cannot mount arbitrary path.')


@provider('s3', prefix='/buckets')
class S3Provider(PosixProvider):
    def mount(self, path):
        path = PosixPath(path)
        if len(path.parts) < 3:
            raise ValueError('Cannot mount all buckets at once.')

        bucket = path.parts[2]
        self.mount_bucket(bucket, path)

    @staticmethod
    def mount_bucket(bucket, path):
        # check whether we should only mount a prefix
        if len(path.parts) > 3:
            bucket = '{}:{}'.format(bucket, PurePath(*path.parts[3:]))

        # create directory for mount point
        path.mkdir(parents=True, exist_ok=True)

        # run goofys
        run(['goofys', bucket, str(path)])
