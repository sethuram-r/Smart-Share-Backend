import configparser

import requests

""" This class handles all the Api calls with User Access Server """


class FileMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__accessDataUrl = config['URL']['ACCESS_DATA_INFO_URL']

    def fetchUserAcessDataForSingleFileFromAccessManagementServer(self, owner, selectedFile):
        parameter = {}
        parameter["owner"] = owner
        parameter["file"] = selectedFile
        response = requests.get(url=self.__accessDataUrl, params=parameter)
        return response.json()["status"]

    def removeUserAccessDetailsForDeletedFiles(self, owner, deletedFiles):
        DeletedFilesOfTheOwner = {}
        DeletedFilesOfTheOwner["owner"] = owner
        DeletedFilesOfTheOwner["files"] = deletedFiles  ### key name should match with the end point
        response = requests.post(url=self.__accessDataUrl, data=DeletedFilesOfTheOwner)
        return response.json()["status"]

    def addUserAccessDetailsForFileorFolderInUserAccessManagementServer(self, accessRecordsToBeInserted):
        response = requests.post(url=self.__accessDataUrl, data=accessRecordsToBeInserted)
        return response.json()["status"]

    def writeOrUpdateUserAccessData(self,
                                    accessRecord):  # similar to creating new access record in api implementation so can use same method
        accessRecordsToBeInserted = {}
        accessRecordsToBeInserted["data"]["access"] = accessRecord
        response = requests.post(url=self.__accessDataUrl, data=accessRecord)
        return response.json()["status"]
