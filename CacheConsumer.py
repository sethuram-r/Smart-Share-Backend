import configparser
from json import loads

from kafka import KafkaConsumer

from CoreService import DataSourceFactory, logging


class CacheConsumer:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._insertCacheTask = config['TASKS']['INSERT_CACHE']
        self._redisRole = config['HELPERS']['REDIS_CACHE']
        self.consumer()

    def insertIntoCache(self, recordsToBeInserted):

        logging.info("Consumer: Inside insertIntoCache")

        redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(role=self._redisRole)

        # Key preparation for Redis begins....

        keyToBeInserted = recordsToBeInserted["bucket"] + '/' + recordsToBeInserted["key"]

        # Key preparation for Redis ends....

        insertionResult = redisConnection.insertObject(keyToBeInserted, recordsToBeInserted["content"])
        if insertionResult == 1:
            logging.info("Error in Cache Insertion %s", recordsToBeInserted)

    def keyDeserializer(self, key):
        return key.decode('utf-8')

    def valueDeserializer(self, value):
        return loads(value.decode('utf-8'))

    def consumer(self):

        consumer = KafkaConsumer(
            'cache',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='core-group'

        )
        for records in consumer:
            if self.keyDeserializer(records.key) == self._insertCacheTask: self.insertIntoCache(
                self.valueDeserializer(records.value))


CacheConsumer()
