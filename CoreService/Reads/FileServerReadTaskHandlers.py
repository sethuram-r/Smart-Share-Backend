import base64
import configparser
import threading

from CoreService import DataSourceFactory, logging
from CoreService.Reads import FileAccessMetaDataApi, ThreadServices, FileStructureTransformer

""" This class handles the tasks that the business needs from the file server or file storage. """


class FileServerReadTaskHandlers:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self._CacheRole = config['HELPERS']['REDIS_CACHE']
        self._insertCacheTask = config['TASKS']['INSERT_CACHE']


    def getLatestContents(self, username, bucketName):

        logging.info("Inside getLatestContents")

        s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()
        resultFromS3 = s3Connection.listObjects(bucketName)
        accesssDetailsForFilesAndFolders = FileAccessMetaDataApi.FileAccessMetaDataApi().fetchUserAcessDataForFilesandFolders()
        fileStructureTransformer = FileStructureTransformer.FileStructureTransformer(username, bucketName,
                                                                                     accesssDetailsForFilesAndFolders)
        hierarchicalStructureForS3result = fileStructureTransformer.transformationProcessPipeline(resultFromS3)

        return hierarchicalStructureForS3result

    def pushTheDownloadedFileToCache(self, s3Data, selectedFileOrFolder, topicName):

        logging.info("Inside pushTheDownloadedFileToCache")

        ThreadServices.ThreadServices().pushToCacheStream(s3Data, selectedFileOrFolder, topicName)



    def getFileOrFolder(self, selectedFileOrFolder, topicName):

        logging.info("Inside getFileOrFolder")

        # topic name level scope is not implemented yet

        redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(self._CacheRole)

        # Key preparation Begins..

        keyToBeSearched = "cache:" + topicName + '/' + selectedFileOrFolder
        # Key preparation Ends..

        if redisConnection.exists(keyToBeSearched) == 1:
            dataFromCache = redisConnection.getObject(keyToBeSearched)
            logging.info("<=============== Returned from Cache ===============>")
            return dataFromCache
        else:
            s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()

            dataFromS3 = s3Connection.getObject(topicName, selectedFileOrFolder)
            dataFromS3InBase64EncodedFromat = base64.standard_b64encode(dataFromS3["Body"].read())
            if dataFromS3InBase64EncodedFromat is not None:
                try:

                    thread = threading.Thread(target=self.pushTheDownloadedFileToCache,
                                              args=(dataFromS3InBase64EncodedFromat, selectedFileOrFolder, topicName,))
                    thread.daemon = True
                    thread.start()
                except:
                    logging.critical("Unable to push into Cache Stream")
            logging.info("<=============== Returned from S3 ===============>")
            return dataFromS3InBase64EncodedFromat
