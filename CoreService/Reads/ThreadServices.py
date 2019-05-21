import configparser
from json import dumps
from time import sleep

from kafka import KafkaProducer

from CoreService import logging, ip, port

""" This class contains tasks / functions which are handled by threads """


class ThreadServices:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._insertCacheTask = config['TASKS']['INSERT_CACHE']  # Doubt whether private variable can be passed or not

    def convertBtyeToExactString(self, byteString):
        return str(byteString).replace("b'", "", 1).replace("'", "").strip()


    def pushToCacheStream(self, s3Data, selectedFileOrFolder, topicName):

        """ Function to submit the signup request to the kafka stream """

        producer = KafkaProducer(bootstrap_servers=[ip + ':' + port], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        # Record Preparation Begins..

        data_to_placed_in_the_stream = {}
        data_to_placed_in_the_stream["content"] = self.convertBtyeToExactString(s3Data)
        data_to_placed_in_the_stream["key"] = selectedFileOrFolder
        data_to_placed_in_the_stream["bucket"] = topicName

        # Record Preparation Ends...

        result = producer.send('cache', key=self._insertCacheTask, value=data_to_placed_in_the_stream)
        sleep(10)
        if result.is_done:
            logging.info("The record have been successfully pushed to the stream")
        else:
            logging.warning("Pushing to the stream have been failed")
