import configparser
import requests


class FileAccessMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.__accessDataUrl = config['URL']['ACCESS_DATA_INFO_URL']
        self.__defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']

    def fetchUserAcessDataForFilesandFolders(self):
        response = requests.get(url=self.__accessDataUrl + "fetchUserAcessDataForFilesandFolders")
        return response.json()
