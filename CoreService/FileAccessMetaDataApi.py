import configparser
import requests


class FileAccessMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__accessDataUrl = config['DEFAULT']['AWS_ACCESS_KEY_ID']

    def fetchUserAcessDataForFilesandFolders(self):
        response = requests.get(url=self.__accessDataUrl)

        print("response------------------>", response)

        return response
