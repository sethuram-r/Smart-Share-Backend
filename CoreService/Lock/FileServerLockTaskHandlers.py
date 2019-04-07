import configparser

from CoreService import DataSourceFactory

""" This class handles the tasks corresponding to the lock server """


class FileServerLockTaskHandlers:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._LockRole = config['HELPERS']['REDIS_LOCK']
        self._redisConnection = DataSourceFactory.DataSourceFactory().getRedisAccess(self._LockRole)

    # There might be problem with key name since bucket name is not tied up from the UI

    def putOrReleaseLock(self, filesOrFoldersToBeLocked):

        """ This function handles the task of putting or releasing the lock on files and folders """

        lockTaskToPerformOnFilesOrFolders = self._redisConnection.lock(filesOrFoldersToBeLocked["task"])
        lockResults = [lockTaskToPerformOnFilesOrFolders(eachFile) for eachFile in filesOrFoldersToBeLocked["data"]]
        if False in lockResults:
            return ({"status": False})
        else:
            return ({"status": True})

    def __checkExistanceOfSelectedFolder(self, Folder):
        return self._redisConnection.exists("lock:" + Folder["key"])

    def currentLockStatus(self, selectedFileOrFolder):  ### Have to be verified ( Rewritten the logic)

        """ This function handles the task of getting the lock status for selected file or folder """

        exists = self.__checkExistanceOfSelectedFolder(selectedFileOrFolder)
        if exists:
            lockStatus = self._redisConnection.lockStatus(selectedFileOrFolder["key"])
            if str(lockStatus).replace("b", "", 1).replace("'", "") == "Yes":
                return ({"status": True})
            else:
                return ({"status": False})
        else:
            return ({"status": True})
