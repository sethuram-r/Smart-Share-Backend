import configparser
from json import loads

from kafka import KafkaConsumer

from CoreService import DataSourceFactory


class RedisConsumer:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._insertCacheTask = config['TASKS']['INSERT_CACHE']
        self._redisRole = config['HELPERS']['REDIS_CACHE']
        self.consumer()

    def insertIntoCache(self, recordsToBeInserted):

        """ Function to insert the user registration details into DB """

        redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(role=self._redisRole)

        # Key preparation for Redis begins....

        keyToBeInserted = recordsToBeInserted["bucket"] + '/' + recordsToBeInserted["key"]

        # Key preparation for Redis ends....

        insertionResult = redisConnection.insertObject(keyToBeInserted, recordsToBeInserted["content"])
        if insertionResult == 1: print(
            "{}------{}----{}".format('Warning', recordsToBeInserted,
                                      'Error in Cache Insertion'))  # logger implementation

    def consumer(self):

        """ This is a kafka consumer that consumes the events and sends to the corresponding event handlers"""

        consumer = KafkaConsumer(
            'authentication',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='core-group',
            key_deserializer=lambda x: (x.decode('utf-8')),
            value_deserializer=lambda x: loads(x.decode('utf-8')))
        for records in consumer:
            print("requests_or_records----------->", records.value)

            """ Based on the key the events are filtered and processed.
             This would have been done by forming a new stream through stream processing using faust"""

            if records.key == self._insertCacheTask: self.insertIntoCache(records.value)
