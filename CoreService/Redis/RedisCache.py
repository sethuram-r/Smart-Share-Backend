import configparser
import datetime

import redis

""" This class gives access to Cache Server which is a Redis Database """


class RedisCache:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        hostName = config['REDIS']['CACHE_HOST']
        port = int(config['REDIS']['CACHE_PORT'])
        db = int(config['REDIS']['DATABASE'])
        self._redisClient = redis.Redis(host=hostName, port=port, db=db)

    def exists(self, key):
        return self._redisClient.exists(key)

    def getObject(self, key):
        return self._redisClient.hmget(key, "content")[0]

    def insertObject(self, key, data):
        row = {"content": data, "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
        insertionResult = self._redisClient.hmset("cache:" + key, row)
        settingExpiryResult = self._redisClient.expire("cache:" + key, 150)
        result = 0 if (insertionResult == True and settingExpiryResult == True) else 1
        return result
