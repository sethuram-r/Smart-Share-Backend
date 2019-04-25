import configparser
import re

from CoreService import DataSourceFactory
from CoreService.Writes import FileMetaDataApi, OtherApiCallsForDifferentServers

""" This class is used to handle tasks corresponding to Transactions"""


class SavepointHandler:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._fileMetaDataApi = FileMetaDataApi.FileMetaDataApi()
        self._otherApiCallsForDifferentServers = OtherApiCallsForDifferentServers.OtherApiCallsForDifferentServers()
        self._fileExtension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        self._transactionRole = config['HELPERS']['REDIS_TRANSACTION']
        self._redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(self._transactionRole)

    def __createSavepointDataFromS3ForEachFile(self, topicName, owner, selectedFile):
        file = {}
        file["key"] = selectedFile
        file["data"] = {}
        if self._fileExtension.search(selectedFile):
            file["data"]["content"] = self._otherApiCallsForDifferentServers.getContentForSelectedFile(topicName,
                                                                                                       selectedFile)
        else:
            file["data"]["content"] = None
        return file

    def createSavepointForUploadOperation(self, topicName, owner, selectedFiles):

        insertionResults = []
        for selectedFile in selectedFiles:
            # Savepoint Creation for each file begins....

            # Step -1 :  Gather User  file content for corresponding file through rest call

            file = self.__createSavepointDataFromS3ForEachFile(topicName, owner, selectedFile)

            # Savepoint insertion begins...

            insertionResult = self._redisConnection.createSavepoint(**file)
            insertionResults.append(insertionResult)
        if False in insertionResults:
            return False
        else:
            return True

    def createSavepointForDeleteOperation(self, owner, selectedFiles):

        insertionResults = []
        for selectedFile in selectedFiles:
            # Savepoint Creation for each file begins....

            # Step -1 :  Gather User access data and file content for corresponding file through rest call

            file = self.__createSavepointDataFromS3ForEachFile(owner, selectedFile["key"])
            file["data"]["access"] = self._fileMetaDataApi.fetchUserAcessDataForSingleFileFromAccessManagementServer(
                owner, selectedFile["key"])

            # Step - 2 Insert the file details to Transaction Database

            # Savepoint insertion begins...

            insertionResult = self._redisConnection.createSavepoint(**file)
            insertionResults.append(insertionResult)
        if False in insertionResults:
            return False
        else:
            return True

    def deleteSavepoint(self, selectedFiles):

        deletionResult = [self._redisConnection.deleteSavepoint(selectedFile) for selectedFile in
                          selectedFiles]  ## have to check response

        return deletionResult

    def rollbackForUploadOperation(self, topicName, filesPresentInTheSavepoint):

        for eachFilesPresentInTheSavepoint in filesPresentInTheSavepoint:
            eachBackupFileWithData = self._redisConnection.getDataForTheFile(eachFilesPresentInTheSavepoint,
                                                                             mapping='data')
            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachBackupFileWithData[
                                                                                                 "key"],
                                                                                             eachBackupFileWithData[
                                                                                                 "data"]["content"])
            if uploadResult == False:
                print("{}------{}----{}".format('Warning', eachBackupFileWithData,
                                                'Error in Rollback for Upload Operation'))  # logger implementation

    def rollBackforDeleteOperation(self, topicName, selectedFiles):

        getAllBackupFilesForSelectedFolder = self._redisConnection.getKeysWithPattern(
            pattern="backup:" + selectedFiles[0]["Key"] + "*")

        print("getAllBackupFilesForSelectedFolder------------->", getAllBackupFilesForSelectedFolder)

        for eachBackupFile in getAllBackupFilesForSelectedFolder:

            eachBackupFileWithData = self._redisConnection.getDataForTheFile(eachBackupFile, mapping='data')

            # step-1 put the access data back

            insertOrUpdateResult = self._fileMetaDataApi.writeOrUpdateUserAccessData(eachBackupFileWithData)

            # step-2 put the S3 data back

            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachBackupFileWithData[
                                                                                                 "key"],
                                                                                             eachBackupFileWithData[
                                                                                                 "data"]["content"])

            if insertOrUpdateResult and uploadResult == False:  # Doubt Condition
                print("{}------{}----{}".format('Warning', eachBackupFile,
                                                'Error in Rollback for Delete operation'))  # logger implementation
