import configparser

import requests

from CoreService import DataSourceFactory

"""This class handles all the Api calls with the READ Server"""


class OtherApiCallsForDifferentServers:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__accessDataUrl = config['URL']['READ_SERVER_URL']
        self._s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()

    def getContentForSelectedFile(self, topicName, fileName):
        """ This function is used to get contents selected file from exposed Read server """
        parameter = {}
        parameter["bucket"] = topicName
        parameter["name"] = fileName
        return requests.get(url=self.__accessDataUrl, params=parameter)

    def writeOrUpdateSavepointInS3(self, bucketName, file, contentOfFile):
        return self._s3Connection.uploadSavepoint(bucketName, file, contentOfFile)