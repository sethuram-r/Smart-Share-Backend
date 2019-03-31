import configparser

from CoreService import FileServerTaskHandlers

""" This class is the core implementation of Business logic done through various task handlers."""


class ServiceImplementation:

    def __init__(self, request):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.username = config['HELPERS']['USER_NAME']
        self.topicName = config['HELPERS']['TOPIC_NAME']
        self.defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']
        self.request = request

    ## getObjects has been renamed to following function name

    def displayCurrentFilesandFoldersForSelectedTopics(self):  # Topic mean Buckets

        """ This function is used to get the files and folders for a particular topic in the network"""

        username = self.request["param"].get(self.username)
        topicName = self.request["param"].get(self.topicName)

        if topicName == None: topicName = self.defaultTopicName

        return FileServerTaskHandlers.FileServerTaskHandlers.getLatestContents(username, topicName)
