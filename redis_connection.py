import datetime

import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def exists(key):
    return redis_client.exists(key)


def get_object(key):
    return redis_client.hmget("cache:" + key, "content")[0]


def insert_object(key, data):
    row = {"content": data, "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
    insertion_result = redis_client.hmset("cache:" + key, row)
    setting_expiry_result = redis_client.expire("cache:" + key, 150)
    if insertion_result == True and setting_expiry_result == True:
        return "Cache inserted or updated"


def insert_lock(key):
    response = redis_client.set("lock:" + key, "No", ex=300)
    return response


def release_lock(key):
    response = redis_client.set("lock:" + key, "Yes")
    return response


def loack_status(key):
    response = redis_client.get("lock:" + key)
    return response


def lock(task):
    if task == "lock":
        return insert_lock
    else:
        return release_lock


def type_of_key(key):
    return redis_client.type(key)
