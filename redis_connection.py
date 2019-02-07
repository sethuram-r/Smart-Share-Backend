import datetime

import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def exists(key):
    return redis_client.exists(key)


def get_object(key):
    return redis_client.hmget(key, "content")[0]


def insert_object(key, data):
    row = {"content": data, "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
    insertion_result = redis_client.hmset("cache:" + key, row)
    setting_expiry_result = redis_client.expire("cache:" + key, 150)
    if insertion_result == True and setting_expiry_result == True:
        return "Cache inserted or updated"


def insert_lock(key):
    response = redis_client.set("lock:" + key, "No", ex=150)
    return response


def release_lock(key):
    """Inside Release lock"""
    response = redis_client.set("lock:" + key, "Yes")
    return response


def lock_status(key):
    response = redis_client.get("lock:" + key)
    return response


def lock(task):
    if task == "lock":
        return insert_lock
    else:
        return release_lock


def type_of_key(key):
    return redis_client.type(key)

def create_savepoint(**arg):
    row = {"content": arg["data"], "timestamp": "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())}
    insertion_result = redis_client.hmset("backup:" + arg["key"], row)
    print(insertion_result)
    return insertion_result

def delete_savepoint(**arg):
    delete_result = redis_client.delete("backup:" + arg["key"])
    return delete_result


def savepoint(task, **arg):
    if task == "lock":
        return create_savepoint, {"key": arg["key"], "data": arg["data"]}
    else:
        return delete_savepoint, {"key": arg["key"]}


def get_keys(pattern):
    return redis_client.keys(pattern)
