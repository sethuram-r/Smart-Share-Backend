import configparser

from CoreService.Redis import RedisCache, RedisLock

"""This class is used to access the Redis Databases. """


class RedisAccess:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.__redisCache = "cache"
        self.__redisLock = "lock"
        self.__redisTransaction = "transaction"


    def getRedisAccess(self, role):

        if role == self.__redisCache: return RedisCache.RedisCache()

        if role == self.__redisLock: return RedisLock.RedisLock()

        # if role == self.__redisTransaction: return RedisTransaction.RedisTransaction()


RedisAccess()
