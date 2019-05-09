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

    def convertBtyeToExactString(self, byteString):
        return str(byteString).replace("b'", "", 1).replace("'", "").strip()

    def pushToCacheStream(self, s3Data, selectedFileOrFolder, topicName):

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                 key_serializer=lambda x: x.encode('utf-8'),
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
        if (result.is_done):
            logging.info("successfully pushed to cache")

    def initiateUploadingProcess(self, owner, filesToBeUploaded, topicName, selectedFolder):
        FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().uploadFilesToDesignatedFolder(owner,
                                                                                                filesToBeUploaded,
                                                                                                topicName,
                                                                                                selectedFolder)
