import configparser
import threading

from CoreService import DataSourceFactory, logging
from CoreService.Writes import SavepointHandler, FileMetaDataApi, ThreadServices, FileStructureTransformer

""" This class handles the tasks that the business needs from the file  server or file storage. """


class FileServerWriteTaskHandlers:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._CacheRole = config['HELPERS']['REDIS_CACHE']
        self._s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()


    def __rollBackSavepointForDeleteOperationInBackground(self, topicName, selectedFiles):
        SavepointHandler.SavepointHandler().rollBackforDeleteOperation(topicName, selectedFiles)

    def __rollBackSavepointForUploadOperationInBackground(self, topicName, selectedFiles):
        SavepointHandler.SavepointHandler().rollbackForUploadOperation(topicName, selectedFiles)

    def _pushFileToCache(self, dataToBePlacedInTheStream):
        ThreadServices.ThreadServices().pushToCacheStream(dataToBePlacedInTheStream)



    def deleteFiles(self, owner, selectedFiles, topicName):

        logging.info("Inside deleteFiles")

        """ This function handles the task of deleting the files in S3 """

        # Savepoint Creation Begins

        filesToBeDeleted = FileStructureTransformer.FileStructureTransformer().extractFileNamesForDeleteOperation(
            selectedFiles)
        folderToCreateSavepoint = FileStructureTransformer.FileStructureTransformer().extractFolderNameForSavepointCreationInDeleteOperation(
            filesToBeDeleted)

        filesToCreateSavepointExtractedFromS3 = self._s3Connection.listObjectsForFolder(bucketName=topicName,
                                                                                        selectedFolder=folderToCreateSavepoint)

        filesToCreateSavepoint = FileStructureTransformer.FileStructureTransformer().transformationProcessPipeline(
            filesToCreateSavepointExtractedFromS3)
        savepointCreatedAndItsFiles = SavepointHandler.SavepointHandler().createSavepointForDeleteOperation(owner,
                                                                                                            filesToCreateSavepoint)
        if savepointCreatedAndItsFiles:

            RecordsToBeDeleted = {}
            RecordsToBeDeleted["Objects"] = selectedFiles
            s3DeletionResults = self._s3Connection.deleteObjects(bucketName=topicName, objects=RecordsToBeDeleted)
            accessDataDeletionResults = FileMetaDataApi.FileMetaDataApi().removeUserAccessDetailsForDeletedFiles(
                owner, selectedFiles)

            if s3DeletionResults and accessDataDeletionResults is True:
                try:
                    savepointCreatedAndItsFiles.clear()
                except:
                    logging.warning("Error unable to delete Savepoint")
                return ({"status": True})
            else:
                logging.info("Inside Rollback for delete operation")
                try:
                    rollBackThread = threading.Thread(
                        target=self.__rollBackSavepointForDeleteOperationInBackground,
                        args=(topicName, savepointCreatedAndItsFiles,))
                    rollBackThread.daemon = True
                    rollBackThread.start()
                    return ({"status": False})
                except:
                    logging.warning("Error unable to Rollback")
        else:
            logging.warning("Error unable to Create Savepoint")
            return ({"status": False})

    def __createAccessRecord(self, owner, eachFileToBeUploaded):

        accessRecord = {}
        accessRecord["owner"] = owner
        accessRecord["file"] = eachFileToBeUploaded["path"] + eachFileToBeUploaded["name"]
        usersAccessingThisRecord = []
        userAccessingThisRecord = {}
        userAccessingThisRecord["name"] = owner
        userAccessingThisRecord["read"] = True
        userAccessingThisRecord["write"] = True
        userAccessingThisRecord["delete"] = True
        usersAccessingThisRecord.append(userAccessingThisRecord)
        accessRecord["accessing_users"] = usersAccessingThisRecord
        return accessRecord

    def convertBtyeToExactString(self, byteString):
        return str(byteString).replace("b'", "", 1).replace("'", "").strip()

    def _cacheRecordFactory(self,s3Data,selectedFileOrFolder,topicName):

        dataToBePlacedInTheStream = {}
        dataToBePlacedInTheStream["content"] = self.convertBtyeToExactString(s3Data)
        dataToBePlacedInTheStream["key"] = selectedFileOrFolder
        dataToBePlacedInTheStream["bucket"] = topicName
        return dataToBePlacedInTheStream


    def __pushFilesToTheCache(self, eachFileToBeUploaded, topicName):

        logging.info(" Thread: Inside __pushFilesToTheCache")

        if (eachFileToBeUploaded["path"] == topicName):
            selectedFileOrFolder = eachFileToBeUploaded["name"]
        else:
            selectedFileOrFolder = eachFileToBeUploaded["path"] + eachFileToBeUploaded["name"]

        try:
            dataToBePlacedInTheStream = self._cacheRecordFactory(eachFileToBeUploaded["file"],selectedFileOrFolder,topicName)
            thread = threading.Thread(target=self._pushFileToCache,
                                      args=(dataToBePlacedInTheStream,))
            thread.daemon = True
            thread.start()
        except:
            logging.critical("Error in Pushing to the stream for Cache Insertion %s", selectedFileOrFolder)
            return False
        return True


    def putTheUploadedFilesToCache(self, filesToBeUploaded, topicName):

        logging.info("Inside putTheUploadedFilesToCache")

        cacheInsertionResults = [self.__pushFilesToTheCache(eachFileToBeUploaded, topicName) for
                                 eachFileToBeUploaded in filesToBeUploaded]
        return cacheInsertionResults

    def accessRecordCreationForEachUploadedFiles(self, owner, filesToBeUploaded):

        logging.info("Inside accessRecordCreationForEachUploadedFiles")

        accessRecordsToBeInserted = [self.__createAccessRecord(owner, eachFileToBeUploaded) for
                                     eachFileToBeUploaded in filesToBeUploaded]

        accessRecordsInsertionResults = [
            FileMetaDataApi.FileMetaDataApi().addUserAccessDetailsForFileorFolderInUserAccessManagementServer(
                eachAccessRecordsToBeInserted) for eachAccessRecordsToBeInserted in accessRecordsToBeInserted]
        return accessRecordsInsertionResults

    def uploadFiles(self, filesToBeUploaded, topicName):

        logging.info("Inside uploadFiles")

        versionIds = [self._s3Connection.uploadObject(eachFileToBeUploaded, topicName) for eachFileToBeUploaded in
                      filesToBeUploaded]
        return versionIds

    def uploadFilesToRootFolder(self, owner, filesToBeUploaded, topicName):

        logging.info("Inside uploadFilesToRootFolder")

        versionIds = self.uploadFiles(filesToBeUploaded, topicName)
        if False not in versionIds:
            accessRecordsInsertionResults = self.accessRecordCreationForEachUploadedFiles(owner, filesToBeUploaded)
            if False not in accessRecordsInsertionResults:
                cacheInsertionResults = self.putTheUploadedFilesToCache(filesToBeUploaded, topicName)
                if False not in cacheInsertionResults:
                    logging.info("Cache Insertion is successful")
        else:
            logging.critical("Uploading to S3 Failed")

    def uploadFilesToDesignatedFolder(self, owner, filesToBeUploaded, topicName, selectedFolder):

        logging.info("Inside uploadFilesToDesignatedFolder")

        if selectedFolder is None:
            return self.uploadFilesToRootFolder(owner, filesToBeUploaded, topicName)
        else:

            filesToCreateSavepointExtractedFromS3 = self._s3Connection.listObjectsForFolder(bucketName=topicName,
                                                                                            selectedFolder=selectedFolder)
            filesToCreateSavepoint = FileStructureTransformer.FileStructureTransformer().transformationProcessPipeline(
                filesToCreateSavepointExtractedFromS3)
            savepointCreatedAndItsFiles = SavepointHandler.SavepointHandler().createSavepointForUploadOperation(
                topicName, owner,
                filesToCreateSavepoint)
            if savepointCreatedAndItsFiles:

                versionIds = self.uploadFiles(filesToBeUploaded, topicName)
                if False not in versionIds:

                    accessRecordsInsertionResults = self.accessRecordCreationForEachUploadedFiles(owner,
                                                                                                  filesToBeUploaded)
                    if False not in accessRecordsInsertionResults:

                        cacheInsertionResults = self.putTheUploadedFilesToCache(filesToBeUploaded, topicName)

                        if False not in cacheInsertionResults:
                            logging.info("Cache Insertion is successful")
                else:

                    try:
                        rollBackThread = threading.Thread(
                            target=self.__rollBackSavepointForUploadOperationInBackground,
                            args=(topicName, savepointCreatedAndItsFiles,))
                        rollBackThread.daemon = True
                        rollBackThread.start()
                    except:
                        logging.warning("Error: unable to Rollback")

                    logging.critical("Uploading to S3 Failed")
            else:
                logging.warning("Savepoint Creation Failed")
