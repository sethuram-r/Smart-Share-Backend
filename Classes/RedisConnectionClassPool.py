import configparser

from Classes import RedisConnectionClass


class RedisConnectionClassPool():

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = int(config['POOL']['MONGO_DB'])
        self._reusables = [RedisConnectionClass.RedisConnectionClass() for _ in range(size)]

    def acquire(self):
        return self._reusables.pop()

    def release(self, reusable):
        self._reusables.append(reusable)
