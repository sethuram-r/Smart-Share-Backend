import configparser

from CoreService.Redis import RedisCache, RedisTransaction, RedisLock

"""This class is used to access the Redis Databases. """


class RedisAccess:

    def __init__(self, role):

        config = configparser.ConfigParser()
        config.read('config.ini')

        if role == config['HELPERS']['REDIS_CACHE']: return RedisCache.RedisCache()

        if role == config['HELPERS']['REDIS_LOCK']: return RedisLock.RedisLock()

        if role == config['HELPERS']['REDIS_TRANSACTION']: return RedisTransaction.RedisTransaction()

# Have to check where it is used....

#
# def type_of_key(self, key):
#     return self.redis_client.type(key)
#
# def get_keys(self, pattern):
#     return self.redis_client.keys(pattern)
