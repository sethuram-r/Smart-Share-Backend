import configparser

from CoreService.Writes import FileServerWriteTaskHandlers

""" This class is the core implementation of Business logic done through various task handlers."""


class ServiceImplementation:

    def __init__(self, request):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.username = config['HELPERS']['USER_NAME']
        self.topicName = config['HELPERS']['TOPIC_NAME']
        self.defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']
        self.selectedFileOrFolder = config['HELPERS']['SELECTED_FILE_OR_FOLDER']
        self.request = request

    ## deleteObjects has been renamed to following function name

    def deleteSelectedFileOrFolders(self):
        """ This function is used to delete the files and folders for a particular topic in the network"""

        selctedFilesToBeDeleted = self.request["data"]
        owner = selctedFilesToBeDeleted["owner"]
        selectedFiles = selctedFilesToBeDeleted["Objects"]
        topicName = selctedFilesToBeDeleted["topicName"]  # have to send bucket details from UI
        return FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().deleteFiles(owner, selectedFiles, topicName)

    def uploadFileOrFolder(self):
        """ This function is used to upload the files and folders for a particular topic in the network """

        dataToBeUploaded = self.request["data"]  # must have topic name from the UI
        owner = dataToBeUploaded["owner"]
        filesToBeUploaded = dataToBeUploaded["data"]
        selectedFolder = filesToBeUploaded["selectedFolder"]  # have to send bucket details from UI
        topicName = dataToBeUploaded["topicName"]  # have to send bucket details from UI
        return FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().deleteFiles(owner, filesToBeUploaded,
                                                                                     topicName, selectedFolder)
