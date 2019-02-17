import configparser

from Classes import AmazonS3Class


class AmazonS3ClassPool():

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = int(config['POOL']['AMAZON_S3'])
        self._reusables = [AmazonS3Class.AmazonS3Class() for _ in range(size)]

    def acquire(self):
        return self._reusables.pop()

    def release(self, reusable):
        self._reusables.append(reusable)
