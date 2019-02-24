import configparser

from Classes import RedisConnectionClass, CommonPool


class RedisConnectionClassPool(CommonPool.CommonPool):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = int(config['POOL']['MONGO_DB'])
        self._reusables = [RedisConnectionClass.RedisConnectionClass() for _ in range(size)]

