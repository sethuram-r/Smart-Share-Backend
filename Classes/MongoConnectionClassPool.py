import configparser

from Classes import MongoConnectionClass


class MongoConnectionClassPool:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = config['POOL']['MONGO_DB']
        self._reusables = [MongoConnectionClass() for _ in range(size)]
