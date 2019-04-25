import configparser

from CoreService.Redis import RedisCache, RedisTransaction, RedisLock

"""This class is used to access the Redis Databases. """


class RedisAccess:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__redisCache = config['HELPERS']['REDIS_CACHE']
        self.__redisLock = config['HELPERS']['REDIS_LOCK']
        self.__redisTransaction = config['HELPERS']['REDIS_TRANSACTION']

    def getRedisAccess(self, role):

        if role == self.__redisCache: return RedisCache.RedisCache()

        if role == self.__redisLock: return RedisLock.RedisLock()

        if role == self.__redisTransaction: return RedisTransaction.RedisTransaction()




# Have to check where it is used....

#
# def type_of_key(self, key):
#     return self.redis_client.type(key)
#
# def get_keys(self, pattern):
#     return self.redis_client.keys(pattern)
