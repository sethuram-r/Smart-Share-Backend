import configparser

from Classes import AmazonS3Class, CommonPool


class AmazonS3ClassPool(CommonPool):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = config['POOL']['AMAZON_S3']
        self._reusables = [AmazonS3Class() for _ in range(size)]
