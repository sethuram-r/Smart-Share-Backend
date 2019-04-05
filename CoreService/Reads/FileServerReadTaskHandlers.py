import configparser
import threading

from CoreService import DataSourceFactory
from CoreService.Reads import FileAccessMetaDataApi, ThreadServices, FileStructureTransformer

""" This class handles the tasks that the business needs from the file server or file storage. """


class FileServerReadTaskHandlers:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._s3 = config['DATA_SOURCE']['AMAZON_S3']  # Doubt whether private variable can be passed or not
        self._CacheRole = config['HELPERS']['REDIS_CACHE']

    def getLatestContents(self, username, bucketName):

        """ This function handles the task of listing the latest files and folders """
        s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()
        resultFromS3 = s3Connection.listObjects(bucketName)
        accesssDetailsForFilesAndFolders = FileAccessMetaDataApi.FileAccessMetaDataApi().fetchUserAcessDataForFilesandFolders()
        fileStructureTransformer = FileStructureTransformer.FileStructureTransformer(username, bucketName,
                                                                                     accesssDetailsForFilesAndFolders)
        hierarchicalStructureForS3result = fileStructureTransformer.transformationProcessPipeline(resultFromS3)

        print("hierarchicalStructureForS3result----------->", hierarchicalStructureForS3result)

        return hierarchicalStructureForS3result

    def getFileOrFolder(self, selectedFileOrFolder, topicName):

        # topic name level scope is not implemented yet

        redisConnection = DataSourceFactory.DataSourceFactory.getS3Access(self._CacheRole)

        # Key preparation Begins..

        keyToBeSearched = "cache:" + topicName + '/' + selectedFileOrFolder

        # Key preparation Ends..

        if redisConnection.exists(keyToBeSearched) == 1:
            dataFromCache = redisConnection.getObject(keyToBeSearched)
            print("returned from cache")
            return dataFromCache
        else:
            s3Connection = DataSourceFactory.DataSourceFactory().getS3Access()
            dataFromS3 = s3Connection.getObject(topicName, selectedFileOrFolder)
            if dataFromS3 is not None:  # Condition has to be checked
                try:
                    thread = threading.Thread(target=ThreadServices.ThreadServices().pushToCacheStream,
                                              args=(dataFromS3, selectedFileOrFolder, topicName,))
                    thread.daemon = True
                    thread.start()
                except:
                    print("Error: unable to push into Cache Stream")
            print("returned from s3")
            return dataFromS3
