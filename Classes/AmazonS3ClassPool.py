import configparser

from Classes import AmazonS3Class


class AmazonS3ClassPool:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = config['POOL']['AMAZON_S3']
        self._reusables = [AmazonS3Class() for _ in range(size)]
