import configparser
import requests


class FileMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.__accessDataUrl = config['URL']['ACCESS_DATA_INFO_URL']

    def fetchUserAcessDataForSingleFileFromAccessManagementServer(self, selectedFile):
        parameter = {}
        parameter["file"] = selectedFile
        response = requests.get(url=self.__accessDataUrl + "fetchUserAcessDataForSingleFileOrFolder",
                                params=parameter).json()
        return response

    def removeUserAccessDetailsForDeletedFiles(self, owner, deletedFiles):
        DeletedFilesOfTheOwner = {}
        DeletedFilesOfTheOwner["owner"] = owner
        DeletedFilesOfTheOwner["files"] = deletedFiles
        response = requests.post(url=self.__accessDataUrl + "removeUserAccessDetailsForDeletedFiles",
                                 json=DeletedFilesOfTheOwner)
        return response.json()["status"]

    def addUserAccessDetailsForFileorFolderInUserAccessManagementServer(self, accessRecordsToBeInserted):
        response = requests.post(url=self.__accessDataUrl + "addUserAccessDetailForFile",
                                 json=accessRecordsToBeInserted)
        return response.json()["status"]

    def writeOrUpdateUserAccessData(self, accessRecord):
        accessRecordsToBeInserted = {}
        accessRecordsToBeInserted["file"] = accessRecord["file"]
        accessRecordsToBeInserted["owner"] = accessRecord["owner"]
        accessRecordsToBeInserted["accessing_users"] = accessRecord["accessingUsers"]
        response = requests.post(url=self.__accessDataUrl + "addUserAccessDetailForFile",
                                 json=accessRecordsToBeInserted)
        return response.json()["status"]
