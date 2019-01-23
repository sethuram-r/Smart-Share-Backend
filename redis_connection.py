import datetime

import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def exists(key):
    return redis_client.exists(key)


def get_object(key):
    return redis_client.hmget(key, "content")[0]


def insert_object(key, data):
    row = {"content": data, "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
    insertion_result = redis_client.hmset(key, row)
    setting_expiry_result = redis_client.expire(key, 150)
    if insertion_result == True and setting_expiry_result == True:
        return "Cache inserted or updated"
