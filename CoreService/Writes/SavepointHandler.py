import configparser
import re
from ast import literal_eval as eval

from CoreService import DataSourceFactory
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
        print("file in __createSavepointDataFromS3ForEachFile----->", file)
        return file

    def createSavepointForUploadOperation(self, topicName, owner, selectedFiles):

        insertionResults = []
        for selectedFile in selectedFiles:
            # Savepoint Creation for each file begins....

            # Step -1 :  Gather User  file content for corresponding file through rest call

            file = self.__createSavepointDataFromS3ForEachFile(topicName, selectedFile)

            print("file-------------->", file)


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
            print("selectedFile------->", selectedFile)
            # Savepoint Creation for each file begins....

            # Step -1 :  Gather User access data and file content for corresponding file through rest call

            file = self.__createSavepointDataFromS3ForEachFile(self.defaultTopicName, selectedFile)
            print("file-------------->", file)
            file["data"]["access"] = self._fileMetaDataApi.fetchUserAcessDataForSingleFileFromAccessManagementServer(
                selectedFile)
            print("file-------------->", file)

            # Step - 2 Insert the file details to Transaction Database

            # Savepoint insertion begins...

            insertionResult = self._redisConnection.createSavepoint(**file)
            insertionResults.append(insertionResult)
        if False in insertionResults:
            return False
        else:
            return True

    def deleteSavepoint(self, selectedFiles):
        print("selectedFiles------------>", selectedFiles)
        print("selectedFiles type -- ", type(selectedFiles))
        for i in selectedFiles:
            print(i)
            print(type(i))

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

    def decodeValuesToString(self, value):
        return value.decode('utf8')

    def convertEachBackupFileWithDataToDictionary(self, eachBackupFileWithData):
        utfDecodedEachBackupFileWithData = self.decodeValuesToString(eachBackupFileWithData)
        return eval(utfDecodedEachBackupFileWithData)



    def rollBackforDeleteOperation(self, topicName, selectedFiles):

        getAllBackupFilesForSelectedFolder = self._redisConnection.getKeysWithPattern(
            pattern="backup:" + selectedFiles[0]["Key"] + "*")

        print("getAllBackupFilesForSelectedFolder------------->", getAllBackupFilesForSelectedFolder)

        for eachBackupFile in getAllBackupFilesForSelectedFolder:

            eachBackupFileKeyWithoutBackupWordInIt = self.decodeValuesToString(eachBackupFile).replace("backup:",
                                                                                                       "").strip()


            eachBackupFileWithData = self._redisConnection.getDataForTheFile(eachBackupFile, mapping='data')
            eachBackupFileWithDataInDictonaryFormat = self.convertEachBackupFileWithDataToDictionary(
                eachBackupFileWithData)

            print("eachBackupFileWithData------->", eachBackupFileWithDataInDictonaryFormat)
            # step-2 put the S3 data back

            uploadResult = self._otherApiCallsForDifferentServers.writeOrUpdateSavepointInS3(topicName,
                                                                                             eachBackupFileKeyWithoutBackupWordInIt,
                                                                                             eachBackupFileWithDataInDictonaryFormat
                                                                                             ["content"])
            print("uploadResult---------->", uploadResult)

            # step-1 put the access data back

            insertOrUpdateResult = self._fileMetaDataApi.writeOrUpdateUserAccessData(
                eachBackupFileWithDataInDictonaryFormat["access"])
            print("insertOrUpdateResult---------->", insertOrUpdateResult)




            if insertOrUpdateResult and uploadResult == False:  # Doubt Condition
                print("{}------{}----{}".format('Warning', eachBackupFile,
                                                'Error in Rollback for Delete operation'))  # logger implementation
