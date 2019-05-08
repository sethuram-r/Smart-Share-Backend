import configparser
import re
from ast import literal_eval as eval

from CoreService import DataSourceFactory, logging
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
        self._redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(self._transactionRole)
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

        insertionResults = []
        for selectedFile in selectedFiles:
            # Savepoint Creation for each file begins....

            # Step -1 :  Gather User  file content for corresponding file through rest call

            file = self.__createSavepointDataFromS3ForEachFile(topicName, selectedFile)

            # Savepoint insertion begins...

            insertionResult = self._redisConnection.createSavepoint(**file)
            insertionResults.append(insertionResult)
        if False in insertionResults:
            return False
        else:
            return True

    def createSavepointForDeleteOperation(self, owner, selectedFiles):

        logging.info("Inside createSavepointForDeleteOperation")

        insertionResults = []
        for selectedFile in selectedFiles:
            # Savepoint Creation for each file begins....

            # Step -1 :  Gather User access data and file content for corresponding file through rest call

            file = self.__createSavepointDataFromS3ForEachFile(self.defaultTopicName, selectedFile)
            file["data"]["access"] = self._fileMetaDataApi.fetchUserAcessDataForSingleFileFromAccessManagementServer(
                selectedFile)
            # Step - 2 Insert the file details to Transaction Database

            # Savepoint insertion begins...

            insertionResult = self._redisConnection.createSavepoint(**file)
            insertionResults.append(insertionResult)
        if False in insertionResults:
            return False
        else:
            return True

    def deleteSavepoint(self, selectedFiles):

        logging.info("Inside deleteSavepoint")

        deletionResult = [self._redisConnection.deleteSavepoint(selectedFile) for selectedFile in
                          selectedFiles]
        return deletionResult

    def rollbackForUploadOperation(self, topicName, filesPresentInTheSavepoint):

        logging.info("Inside rollbackForUploadOperation")

        for eachFilesPresentInTheSavepoint in filesPresentInTheSavepoint:
            eachBackupFileWithData = self._redisConnection.getDataForTheFile(eachFilesPresentInTheSavepoint,
                                                                             mapping='data')
            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachBackupFileWithData[
                                                                                                 "key"],
                                                                                             eachBackupFileWithData[
                                                                                                 "data"]["content"])
            if uploadResult == False:
                logging.warning('Error in Rollback for Upload Operation %s', eachBackupFileWithData)

    def decodeValuesToString(self, value):
        return value.decode('utf8')

    def convertEachBackupFileWithDataToDictionary(self, eachBackupFileWithData):
        utfDecodedEachBackupFileWithData = self.decodeValuesToString(eachBackupFileWithData)
        return eval(utfDecodedEachBackupFileWithData)



    def rollBackforDeleteOperation(self, topicName, selectedFiles):

        logging.info("Inside rollBackforDeleteOperation")

        getAllBackupFilesForSelectedFolder = self._redisConnection.getKeysWithPattern(
            pattern="backup:" + selectedFiles[0]["Key"] + "*")

        for eachBackupFile in getAllBackupFilesForSelectedFolder:
            eachBackupFileKeyWithoutBackupWordInIt = self.decodeValuesToString(eachBackupFile).replace("backup:",
                                                                                                       "").strip()
            eachBackupFileWithData = self._redisConnection.getDataForTheFile(eachBackupFile, mapping='data')
            eachBackupFileWithDataInDictonaryFormat = self.convertEachBackupFileWithDataToDictionary(
                eachBackupFileWithData)

            # step-2 put the S3 data back

            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachBackupFileKeyWithoutBackupWordInIt,
                                                                                             eachBackupFileWithDataInDictonaryFormat
                                                                                             ["content"])
            # step-1 put the access data back

            insertOrUpdateResult = self._fileMetaDataApi.writeOrUpdateUserAccessData(
                eachBackupFileWithDataInDictonaryFormat["access"])

            if insertOrUpdateResult and uploadResult == False:
                logging.warning('Error in Rollback for Delete Operation %s', eachBackupFile)
