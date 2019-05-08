import configparser
import requests

from CoreService import logging


class FileAccessMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.__accessDataUrl = config['URL']['ACCESS_DATA_INFO_URL']
        self.__defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']

    def fetchUserAcessDataForFilesandFolders(self):
        logging.info("Inside fetchUserAcessDataForFilesandFolders")

        response = requests.get(url=self.__accessDataUrl + "fetchUserAcessDataForFilesAndFolders")
        return response.json()
