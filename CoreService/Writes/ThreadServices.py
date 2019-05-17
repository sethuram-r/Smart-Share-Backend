import configparser
from json import dumps
from time import sleep

from kafka import KafkaProducer

from CoreService import logging
from CoreService.Writes import FileServerWriteTaskHandlers

""" This class contains tasks / functions which are handled by threads """

class ThreadServices:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._insertCacheTask = config['TASKS'][
            'INSERT_CACHE']
        self._producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                 key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))


    def pushToCacheStream(self, dataToBePlacedInTheStream):

        result = self._producer.send("quick-access",key = self._insertCacheTask,value=dataToBePlacedInTheStream)
        sleep(5)
        if (result.is_done):
            logging.info("successfully pushed to cache")

    def initiateUploadingProcess(self, owner, filesToBeUploaded, topicName, selectedFolder):
        FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().uploadFilesToDesignatedFolder(owner,
                                                                                                filesToBeUploaded,
                                                                                                topicName,
                                                                                                selectedFolder)
