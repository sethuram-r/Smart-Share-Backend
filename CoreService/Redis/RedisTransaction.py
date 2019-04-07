import configparser
import datetime

import redis

""" This class gives access to Transaction Server which is a Redis Database """


class RedisTransaction:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('config.ini')
        hostName = config['REDIS']['TRANSACTION_HOST']
        port = int(config['REDIS']['TRANSACTION_PORT'])
        db = int(config['REDIS']['DATABASE'])
        self._redisClient = redis.Redis(host=hostName, port=port, db=db)

    def createSavepoint(self, **arg):
        row = {"data": arg["data"], "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
        insertionResult = self._redisClient.hmset("backup:" + arg["key"], row)
        settingExpiryResult = self._redisClient.expire("backup:" + arg["key"], 200)
        overallresult = True if (insertionResult == True and settingExpiryResult == True) else False
        return overallresult


    def deleteSavepoint(self, **arg):
        deleteResult = self._redisClient.delete("backup:" + arg["key"])
        return deleteResult

    def getKeysWithPattern(self, pattern):
        return self._redisClient.keys(pattern)

    def getDataForTheFile(self, key, mapping):
        return self._redisClient.hmget(key, mapping)[0]
