from flask import Flask

from CoreService.Cache import RedisConsumer

app = Flask("Cache Server")


def cacheConsumer():
    RedisConsumer.RedisConsumer()


cacheConsumer()
