import configparser

import redis

""" This class gives access to Lock Server which is a Redis Database """


class RedisLock:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        hostName = config['REDIS']['LOCK_HOST']
        port = int(config['REDIS']['LOCK_PORT'])
        db = int(config['REDIS']['DATABASE'])
        self._redisClient = redis.Redis(host=hostName, port=port, db=db)

    def insertLock(self, key):
        response = self._redisClient.set("lock:" + key, "No", ex=60)
        return response

    def releaseLock(self, key):
        response = self._redisClient.set("lock:" + key, "Yes")
        return response

    def lockStatus(self, key):
        response = self._redisClient.get("lock:" + key)
        return response

    def lock(self, task):
        if task == "lock":
            return self.insertLock
        else:
            return self.releaseLock

    def exists(self, key):
        return self._redisClient.exists(key)
