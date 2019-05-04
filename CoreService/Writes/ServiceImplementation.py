import configparser

from CoreService.Writes import FileServerWriteTaskHandlers

""" This class is the core implementation of Business logic done through various task handlers."""


class ServiceImplementation:

    def __init__(self, request):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.username = config['HELPERS']['USER_NAME']
        self.topicName = config['HELPERS']['TOPIC_NAME']
        self.defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']
        self.selectedFileOrFolder = config['HELPERS']['SELECTED_FILE_OR_FOLDER']
        self.request = request



    def deleteSelectedFileOrFolders(self):

        selctedFilesToBeDeleted = self.request["data"]
        owner = selctedFilesToBeDeleted["owner"]
        selectedFiles = selctedFilesToBeDeleted["Objects"]
        topicName = self.defaultTopicName
        return FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().deleteFiles(owner, selectedFiles, topicName)

    def uploadFileOrFolder(self):
        dataToBeUploaded = self.request["data"]
        owner = dataToBeUploaded["owner"]
        filesToBeUploaded = dataToBeUploaded["data"]
        selectedFolder = dataToBeUploaded["selectedFolder"]
        topicName = self.defaultTopicName
        uploadResult = FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().uploadFilesToDesignatedFolder(owner,
                                                                                                               filesToBeUploaded,
                                                                                     topicName, selectedFolder)
        print("uploadResult-------", uploadResult)
        return uploadResult
