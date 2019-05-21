import configparser
import re

from CoreService import logging
from CoreService.Writes import FileMetaDataApi, OtherApiCallsForDifferentServers

""" This class is used to handle tasks corresponding to Transactions"""


class SavepointHandler:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._fileMetaDataApi = FileMetaDataApi.FileMetaDataApi()
        self._otherApiCallsForDifferentServers = OtherApiCallsForDifferentServers.OtherApiCallsForDifferentServers()
        self._fileExtension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        self._transactionRole = config['HELPERS']['REDIS_TRANSACTION']
        # self._redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(self._transactionRole)
        self.defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']

    def __createSavepointDataFromS3ForEachFile(self, topicName, selectedFile):
        file = {}
        file["key"] = selectedFile
        file["data"] = {}
        if self._fileExtension.search(selectedFile):
            file["data"]["content"] = self._otherApiCallsForDifferentServers.getContentForSelectedFile(topicName,
                                                                                                       selectedFile)
        else:
            file["data"]["content"] = ""
        return file

    def createSavepointForUploadOperation(self, topicName, owner, selectedFiles):

        logging.info("Inside createSavepointForUploadOperation")

        filesCreatedAtSavepointDuringUploadOperation = []
        for selectedFile in selectedFiles:
            file = self.__createSavepointDataFromS3ForEachFile(topicName, selectedFile)
            filesCreatedAtSavepointDuringUploadOperation.append(file)

        return filesCreatedAtSavepointDuringUploadOperation


    def createSavepointForDeleteOperation(self, owner, selectedFiles):

        logging.info("Inside createSavepointForDeleteOperation")

        filesCreatedAtSavepointDuringDeleteOperation = []
        for selectedFile in selectedFiles:

            file = self.__createSavepointDataFromS3ForEachFile(self.defaultTopicName, selectedFile)
            file["data"]["access"] = self._fileMetaDataApi.fetchUserAcessDataForSingleFileFromAccessManagementServer(
                selectedFile)
            filesCreatedAtSavepointDuringDeleteOperation.append(file)

        return filesCreatedAtSavepointDuringDeleteOperation


    def rollbackForUploadOperation(self, topicName, filesPresentInTheSavepoint):

        logging.info("Inside rollbackForUploadOperation")

        for eachFilePresentInTheSavepoint in filesPresentInTheSavepoint:
            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachFilePresentInTheSavepoint[
                                                                                                 "key"],
                                                                                             eachFilePresentInTheSavepoint[
                                                                                                 "data"]["content"])
            if uploadResult == False:
                logging.warning('Error in Rollback for Upload Operation %s', eachFilePresentInTheSavepoint)

    def rollBackforDeleteOperation(self, topicName, filesPresentInTheSavepoint):

        logging.info("Inside rollBackforDeleteOperation")

        for eachBackupFile in filesPresentInTheSavepoint:

            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachBackupFile["key"],
                                                                                             eachBackupFile["data"]
                                                                                             ["content"])
            insertOrUpdateResult = self._fileMetaDataApi.writeOrUpdateUserAccessData(
                eachBackupFile["data"]["access"])
            if insertOrUpdateResult and uploadResult == False:
                logging.warning('Error in Rollback for Delete Operation %s', eachBackupFile)
