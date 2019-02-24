import configparser

from Classes import MongoConnectionClass, CommonPool


class MongoConnectionClassPool(CommonPool.CommonPool):


    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        size = int(config['POOL']['MONGO_DB'])
        self._reusables = [MongoConnectionClass.MongoConnectionClass() for _ in range(size)]


