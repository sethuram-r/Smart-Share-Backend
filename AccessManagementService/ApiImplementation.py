import configparser

from AccessManagementService import logging
from AccessManagementService.PostgresCommunicator import PostgresWriteTaskHandler, PostgresReadTaskHandler


class ApiImplmentation:
    def __init__(self, request, modelInstance, databaseInstance):
        config = configparser.ConfigParser()
        config.read('AccessManagementConfig.ini')
        self.request = request
        self.modelInstance = modelInstance
        self.databaseInstance = databaseInstance

    def fetchUserAcessDataForFilesAndFolders(self):
        logging.info("Inside fetchUserAcessDataForFilesAndFolders")

        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).fetchUserAcessDataForFilesandFoldersInDictionaryFormat()

    def fetchUserAcessDataForSingleFileOrFolder(self):
        logging.info("Inside fetchUserAcessDataForSingleFileOrFolder")

        fileName = self.request["param"].get('file')
        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).fetchUserAcessDataForSingleFileOrFolderInDictionaryFormat(
            fileName)

    def removeUserAccessDetailsForDeletedFiles(self):
        logging.info("Inside removeUserAccessDetailsForDeletedFiles")

        accessRecordsToBeDeleted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                 self.databaseInstance).deleteAccessDetailForFiles(
            accessRecordsToBeDeleted["files"])

    def addUserAccessDetailForFile(self):
        logging.info("Inside addUserAccessDetailForFile")

        accessRecordToBeInserted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                 self.databaseInstance).createUserAccessDetailForFile(
            accessRecordToBeInserted)
