import base64
import configparser
from json import dumps

from kafka import KafkaProducer

""" This class contains tasks / functions which are handled by threads """


class ThreadServices:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._insertCacheTask = config['TASKS']['INSERT_CACHE']  # Doubt whether private variable can be passed or not

    def pushToCacheStream(self, s3Data, selectedFileOrFolder, topicName):

        """ Function to submit the signup request to the kafka stream """

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        # Record Preparation Begins..

        base64EncodedValue = base64.standard_b64encode(s3Data["Body"].read())

        data_to_placed_in_the_stream = {}
        data_to_placed_in_the_stream["content"] = base64EncodedValue
        data_to_placed_in_the_stream["key"] = selectedFileOrFolder
        data_to_placed_in_the_stream["bucket"] = topicName

        # Record Preparation Ends...

        result = producer.send('cache', key=self._insertCacheTask, value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})
