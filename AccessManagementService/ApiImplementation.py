import configparser

from AccessManagementService import logging
from AccessManagementService.PostgresCommunicator import PostgresWriteTaskHandler, PostgresReadTaskHandler


class ApiImplmentation:
    def __init__(self, request):
        config = configparser.ConfigParser()
        config.read('AccessManagementConfig.ini')
        self.request = request
        # self.modelInstance = modelInstance
        # self.databaseInstance = databaseInstance

    def fetchUserAcessDataForFilesAndFolders(self):
        logging.info("Inside fetchUserAcessDataForFilesAndFolders")

        return PostgresReadTaskHandler.PostgresReadTaskHandler().fetchUserAcessDataForFilesandFoldersInDictionaryFormat()

    def fetchUserAcessDataForSingleFileOrFolder(self):
        logging.info("Inside fetchUserAcessDataForSingleFileOrFolder")

        fileName = self.request["param"].get('file')
        return PostgresReadTaskHandler.PostgresReadTaskHandler().fetchUserAcessDataForSingleFileOrFolderInDictionaryFormat(
            fileName)

    def removeUserAccessDetailsForDeletedFiles(self):
        logging.info("Inside removeUserAccessDetailsForDeletedFiles")

        accessRecordsToBeDeleted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler().deleteAccessDetailForFiles(
            accessRecordsToBeDeleted["files"])

    def addUserAccessDetailForFile(self):
        logging.info("Inside addUserAccessDetailForFile")

        accessRecordToBeInserted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler().createUserAccessDetailForFile(
            accessRecordToBeInserted)
