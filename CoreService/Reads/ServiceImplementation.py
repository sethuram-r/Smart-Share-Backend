import configparser

from CoreService.Reads import FileServerReadTaskHandlers

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

    def displayCurrentFilesandFoldersForSelectedTopics(self):

        username = self.request["param"].get(self.username)
        topicName = self.request["param"].get(self.topicName)
        if topicName == None: topicName = self.defaultTopicName
        return FileServerReadTaskHandlers.FileServerReadTaskHandlers().getLatestContents(username, topicName)

    def downloadSelectedFileOrFolders(self):

        selectedFileOrFolder = self.request["param"].get(self.selectedFileOrFolder)
        topicName = self.request["param"].get(self.topicName)
        if topicName == None: topicName = self.defaultTopicName
        return FileServerReadTaskHandlers.FileServerReadTaskHandlers().getFileOrFolder(selectedFileOrFolder, topicName)
