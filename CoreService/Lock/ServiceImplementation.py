import configparser

from CoreService.Lock import FileServerLockTaskHandlers

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

    ## lockObjects has been renamed to following function name

    def lockFileOrFolder(self):
        """ This function is used to put and release the lock for request file or folders """

        filesOrFoldersToBeLocked = self.request["data"]
        return FileServerLockTaskHandlers.FileServerLockTaskHandlers().putOrReleaseLock(filesOrFoldersToBeLocked)

    ## lockStatus has been renamed to following function name

    def getCurrentLockStatusForSelectedFolder(self):
        """ This function is used to get the lock status for selected file or folder for a the lock server """

        filesOrFoldersToBeChecked = self.request["data"]
        return FileServerLockTaskHandlers.FileServerLockTaskHandlers().currentLockStatus(filesOrFoldersToBeChecked)
