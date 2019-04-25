import configparser
import threading

from CoreService import DataSourceFactory
from CoreService.Writes import SavepointHandler, FileMetaDataApi, ThreadServices

""" This class handles the tasks that the business needs from the file  server or file storage. """


class FileServerWriteTaskHandlers:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._CacheRole = config['HELPERS']['REDIS_CACHE']
        self._s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()

    def deleteFiles(self, owner, selectedFiles, topicName):

        """ This function handles the task of deleting the files in S3 """

        # Savepoint Creation Begins
        savepointCreated = SavepointHandler.SavepointHandler().createSavepointForDeleteOperation(owner, selectedFiles)
        if savepointCreated:

            # Step -1 Delete files in S3

            # Delete Record Preparation Begins ...

            RecordsToBeDeleted = {}
            RecordsToBeDeleted["Objects"] = selectedFiles

            # Delete Record Preparation Ends ...

            s3DeletionResults = self._s3Connection.deleteObjects(bucketName=topicName, objects=RecordsToBeDeleted)
            # Delete Access Files in the User Access Table
            accessDataDeletionResults = FileMetaDataApi.FileMetaDataApi().removeUserAccessDetailsForDeletedFiles(owner,
                                                                                                                 selectedFiles)
            if s3DeletionResults and accessDataDeletionResults == True:  # doubt condition

                try:
                    deleteSavepointThread = threading.Thread(target=SavepointHandler.SavepointHandler().deleteSavepoint,
                                                             args=(selectedFiles,))
                    deleteSavepointThread.daemon = True
                    deleteSavepointThread.start()
                    # savepointDeleted = SavepointHandler.SavepointHandler().deleteSavepoint(selectedFiles)
                except:
                    print("Error unable to delete Savepoint")
                return ({"status": True})
            else:

                try:
                    rollBackThread = threading.Thread(
                        target=SavepointHandler.SavepointHandler().rollBackforDeleteOperation,
                        args=(topicName, selectedFiles,))
                    rollBackThread.daemon = True
                    rollBackThread.start()
                except:
                    print("Error: unable to Rollback")

                return ({"status": False})
        else:
            print("Error: unable to Create Savepoint")
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

    def __pushFilesToTheCache(self, eachFileToBeUploaded, topicName):

        """ Thread to push uploaded file to cache stream """

        if (eachFileToBeUploaded["path"] == topicName):
            selectedFileOrFolder = eachFileToBeUploaded["name"]
        else:
            selectedFileOrFolder = eachFileToBeUploaded["path"] + eachFileToBeUploaded["name"]

        try:
            thread = threading.Thread(target=ThreadServices.ThreadServices().pushToCacheStream,
                                      args=(eachFileToBeUploaded["file"], selectedFileOrFolder, topicName,))
            thread.daemon = True
            thread.start()
        except:
            print(
                "{}------{}----{}".format('Warning', selectedFileOrFolder,
                                          'Error in Pushing to the stream for Cache Insertion'))  # logger implementation
            return False
        return True

    def uploadFiles(self, owner, filesToBeUploaded, topicName, selectedFolder):

        """ This function handles the task of uploading the files in S3 """

        # Get Files for the Root Folder

        filesToCreateSavepoint = self._s3Connection.listObjectsForFolder(bucketName=topicName, prefix=selectedFolder)

        # Savepoint Creation Begins

        savepointCreated = SavepointHandler.SavepointHandler().createSavepointForUploadOperation(topicName, owner,
                                                                                                 filesToCreateSavepoint)

        if savepointCreated:

            # Step -1 Upload file in S3

            versionIds = [self._s3Connection.uploadObject(eachFileToBeUploaded, topicName) for eachFileToBeUploaded in
                          filesToBeUploaded]

            if False not in versionIds:
                accessRecordsToBeInserted = [self.__createAccessRecord(owner, eachFileToBeUploaded) for
                                             eachFileToBeUploaded in filesToBeUploaded]
                accessRecordsInsertionResults = FileMetaDataApi.FileMetaDataApi().addUserAccessDetailsForFileorFolderInUserAccessManagementServer(
                    accessRecordsToBeInserted)

                if accessRecordsInsertionResults:
                    cacheInsertionResults = [self.__pushFilesToTheCache(eachFileToBeUploaded, topicName) for
                                             eachFileToBeUploaded in filesToBeUploaded]
                    if False not in cacheInsertionResults:  # this condition might not be needed can assume that this will always happen
                        try:
                            deleteSavepointThread = threading.Thread(
                                target=SavepointHandler.SavepointHandler().deleteSavepoint,
                                args=(filesToCreateSavepoint,))
                            deleteSavepointThread.daemon = True
                            deleteSavepointThread.start()
                            # savepointDeleted = SavepointHandler.SavepointHandler().deleteSavepoint(selectedFiles)
                        except:
                            print("Error unable to delete Savepoint")
                        return ({"status": True})
            else:
                try:
                    rollBackThread = threading.Thread(
                        target=SavepointHandler.SavepointHandler().rollbackForUploadOperation,
                        args=(topicName, filesToCreateSavepoint,))
                    rollBackThread.daemon = True
                    rollBackThread.start()
                except:
                    print("Error: unable to Rollback")

                return ({"status": False})

        else:
            return ({"status": False})
