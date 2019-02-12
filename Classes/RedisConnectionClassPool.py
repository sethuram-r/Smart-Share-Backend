import configparser

from Classes import RedisConnectionClass, CommonPool


class RedisConnectionClassPool(CommonPool):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = config['POOL']['MONGO_DB']
        self._reusables = [RedisConnectionClass() for _ in range(size)]
