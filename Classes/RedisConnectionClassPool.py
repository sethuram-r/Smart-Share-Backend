import configparser

from Classes import RedisConnectionClass


class RedisConnectionClassPool:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = config['POOL']['MONGO_DB']
        self._reusables = [RedisConnectionClass() for _ in range(size)]
