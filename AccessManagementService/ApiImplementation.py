import configparser

from AccessManagementService.PostgresCommunicator import PostgresWriteTaskHandler, PostgresReadTaskHandler


class ApiImplmentation:
    def __init__(self, request, modelInstance, databaseInstance):
        config = configparser.ConfigParser()
        config.read('AccessManagementConfig.ini')
        self.request = request
        self.modelInstance = modelInstance
        self.databaseInstance = databaseInstance

    def fetchUserAcessDataForFilesandFolders(self):
        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).fetchUserAcessDataForFilesandFoldersInDictionaryFormat()

    def fetchUserAcessDataForSingleFileOrFolder(self):
        fileName = self.request["param"].get('file')
        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).fetchUserAcessDataForSingleFileOrFolderInDictionaryFormat(
            fileName)

    def removeUserAccessDetailsForDeletedFiles(self):
        accessRecordsToBeDeleted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                 self.databaseInstance).deleteAccessDetailForFiles(
            accessRecordsToBeDeleted["files"])

    def addUserAccessDetailForFile(self):
        accessRecordToBeInserted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                 self.databaseInstance).createUserAccessDetailForFile(
            accessRecordToBeInserted)
