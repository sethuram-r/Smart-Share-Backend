import configparser
import requests

from CoreService import logging


class FileMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.__accessDataUrl = config['URL']['ACCESS_DATA_INFO_URL']

    def fetchUserAcessDataForSingleFileFromAccessManagementServer(self, selectedFile):
        logging.info("Inside fetchUserAcessDataForSingleFileFromAccessManagementServer")

        parameter = {}
        parameter["file"] = selectedFile
        response = requests.get(url=self.__accessDataUrl + "fetchUserAcessDataForSingleFileOrFolder",
                                params=parameter).json()
        return response

    def removeUserAccessDetailsForDeletedFiles(self, owner, deletedFiles):
        logging.info("Inside removeUserAccessDetailsForDeletedFiles")

        DeletedFilesOfTheOwner = {}
        DeletedFilesOfTheOwner["owner"] = owner
        DeletedFilesOfTheOwner["files"] = deletedFiles
        response = requests.post(url=self.__accessDataUrl + "removeUserAccessDetailsForDeletedFiles",
                                 json=DeletedFilesOfTheOwner)
        return response.json()["status"]

    def addUserAccessDetailsForFileorFolderInUserAccessManagementServer(self, accessRecordsToBeInserted):
        logging.info("Inside addUserAccessDetailsForFileorFolderInUserAccessManagementServer")

        response = requests.post(url=self.__accessDataUrl + "addUserAccessDetailForFile",
                                 json=accessRecordsToBeInserted)
        return response.json()["status"]

    def writeOrUpdateUserAccessData(self, accessRecord):
        logging.info("Inside writeOrUpdateUserAccessData")

        accessRecordsToBeInserted = {}
        accessRecordsToBeInserted["file"] = accessRecord["file"]
        accessRecordsToBeInserted["owner"] = accessRecord["owner"]
        accessRecordsToBeInserted["accessing_users"] = accessRecord["accessingUsers"]
        response = requests.post(url=self.__accessDataUrl + "addUserAccessDetailForFile",
                                 json=accessRecordsToBeInserted)
        return response.json()["status"]
