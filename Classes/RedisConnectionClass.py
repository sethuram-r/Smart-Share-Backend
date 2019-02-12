import configparser
import datetime

import redis


class RedisConnectionClass:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        host_name = config['REDIS']['HOST']
        port = int(config['REDIS']['PORT'])
        db = int(config['REDIS']['DATABASE'])
        self.redis_client = redis.Redis(host=host_name, port=port, db=db)

    def exists(self, key):
        return self.redis_client.exists(key)

    def get_object(self, key):
        return self.redis_client.hmget(key, "content")[0]

    def insert_object(self, key, data):
        row = {"content": data, "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
        insertion_result = self.redis_client.hmset("cache:" + key, row)
        setting_expiry_result = self.redis_client.expire("cache:" + key, 150)
        if insertion_result == True and setting_expiry_result == True:
            return "Cache inserted or updated"

    def insert_lock(self, key):
        response = self.redis_client.set("lock:" + key, "No", ex=150)
        return response

    def release_lock(self, key):
        """Inside Release lock"""
        response = self.redis_client.set("lock:" + key, "Yes")
        return response

    def lock_status(self, key):
        response = self.redis_client.get("lock:" + key)
        return response

    def lock(self, task):
        if task == "lock":
            return self.insert_lock
        else:
            return self.release_lock

    def type_of_key(self, key):
        return self.redis_client.type(key)

    def create_savepoint(self, **arg):
        row = {"content": arg["data"], "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
        insertion_result = self.redis_client.hmset("backup:" + arg["key"], row)
        print(insertion_result)
        return insertion_result

    def delete_savepoint(self, **arg):
        delete_result = self.redis_client.delete("backup:" + arg["key"])
        return delete_result

    def savepoint(self, task, **arg):
        if task == "lock":
            return self.create_savepoint, {"key": arg["key"], "data": arg["data"]}
        else:
            return self.delete_savepoint, {"key": arg["key"]}

    def get_keys(self, pattern):
        return self.redis_client.keys(pattern)
