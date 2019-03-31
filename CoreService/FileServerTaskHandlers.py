import configparser

from CoreService import DataSourceFactory, FileStructureTransformer, FileAccessMetaDataApi

""" This class handles the tasks that the business needs from the file server or file storage. """


class FileServerTaskHandlers:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._s3 = config['DATA_SOURCE']['AMAZON_S3']  # Doubt whether private variable can be passed or not

    def getLatestContents(self, username, bucketName):
        s3Connection = DataSourceFactory.DataSourceFactory.getS3Access()
        resultFromS3 = s3Connection.listObjects(bucketName)
        accesssDetailsForFilesAndFolders = FileAccessMetaDataApi.FileAccessMetaDataApi.fetchUserAcessDataForFilesandFolders()
        fileStructureTransformer = FileStructureTransformer.FileStructureTransformer(username, bucketName,
                                                                                     accesssDetailsForFilesAndFolders)
        hierarchicalStructureForS3result = fileStructureTransformer.transformationProcessPipeline(resultFromS3)

        print("hierarchicalStructureForS3result----------->", hierarchicalStructureForS3result)

        return hierarchicalStructureForS3result
