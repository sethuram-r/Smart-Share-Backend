import configparser
import threading

from CoreService import logging
from CoreService.Writes import FileServerWriteTaskHandlers, ThreadServices

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

    def _initiateUploading(self, owner, filesToBeUploaded, topicName, selectedFolder):
        ThreadServices.ThreadServices().initiateUploadingProcess(owner, filesToBeUploaded, topicName, selectedFolder)

    def deleteSelectedFileOrFolders(self):
        logging.info("Inside deleteSelectedFileOrFolders")

        selctedFilesToBeDeleted = self.request["data"]
        owner = selctedFilesToBeDeleted["owner"]
        selectedFiles = selctedFilesToBeDeleted["Objects"]
        topicName = self.defaultTopicName
        return FileServerWriteTaskHandlers.FileServerWriteTaskHandlers().deleteFiles(owner, selectedFiles, topicName)

    def uploadFileOrFolder(self):
        logging.info("Inside uploadFileOrFolder")

        dataToBeUploaded = self.request["data"]
        owner = dataToBeUploaded["owner"]
        filesToBeUploaded = dataToBeUploaded["data"]
        selectedFolder = dataToBeUploaded["selectedFolder"]
        topicName = self.defaultTopicName
        try:
            uploadInitializationThread = threading.Thread(target=self._initiateUploading,
                                                          args=(owner, filesToBeUploaded, topicName, selectedFolder,))
            uploadInitializationThread.daemon = True
            uploadInitializationThread.start()
            return ({"status": True})
        except:
            logging.warning("Error unable to delete Savepoint")
            return ({"status": False})
