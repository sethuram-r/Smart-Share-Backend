import configparser
from json import loads

from kafka import KafkaConsumer

from CoreService import DataSourceFactory, logging

config = configparser.ConfigParser()
config.read('CoreConfig.ini')
_insertCacheTask = config['TASKS']['INSERT_CACHE']
_redisRole = config['HELPERS']['REDIS_CACHE']


def _insertIntoCache(recordsToBeInserted):
    logging.info("Consumer: Inside insertIntoCache")

    redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(role=_redisRole)

    keyToBeInserted = recordsToBeInserted["bucket"] + '/' + recordsToBeInserted["key"]

    insertionResult = redisConnection.insertObject(keyToBeInserted, recordsToBeInserted["content"])
    if insertionResult == 1:
        logging.info("Error in Cache Insertion %s", recordsToBeInserted)


def consumer():
    consumer = KafkaConsumer(
        'quick-access',
        bootstrap_servers=['localhost:9092'],
        enable_auto_commit=True,
        group_id='cache-consumers',
        key_deserializer=lambda x: (x.decode('utf-8')),
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    for record in consumer:
        print(record.value)
        if record.key == _insertCacheTask: _insertIntoCache(record.value)

consumer()
