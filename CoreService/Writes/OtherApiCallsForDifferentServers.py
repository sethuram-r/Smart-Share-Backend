import configparser
import requests

from CoreService import DataSourceFactory, logging

"""This class handles all the Api calls with the READ Server"""


class OtherApiCallsForDifferentServers:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._readServerUrl = config['URL']['READ_SERVER_URL']
        self._s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()

    def getContentForSelectedFile(self, topicName, fileName):
        logging.info("Inside getContentForSelectedFile")

        parameter = {}
        parameter["topicName"] = topicName
        parameter["key"] = fileName
        contentOfSelectedFile = requests.get(url=self._readServerUrl + "downloadSelectedFileOrFolders",
                                             params=parameter)
        return contentOfSelectedFile.text


    def writeOrUpdateSavepointInS3(self, bucketName, file, contentOfFile):
        logging.info("Inside writeOrUpdateSavepointInS3")

        return self._s3Connection.uploadSavepoint(bucketName, file, contentOfFile)
