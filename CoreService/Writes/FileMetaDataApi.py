import configparser
import requests

""" This class handles all the Api calls with the READ Server and User Access Server"""


class FileMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__accessDataUrl = config['DEFAULT']['AWS_ACCESS_KEY_ID']  # have to change

    def fetchUserAcessDataForFile(self, owner, selectedFile):
        """ This function is used to get user access data for selected file from exposed users_access_data table"""

        response = requests.get(url=self.__accessDataUrl)

        print("response------------------>", response)

        return response

    def getContentForSelectedFile(self, fileName):
        """ This function is used to get contents selected file from exposed Read server """

        pass

    def removeUserAccessDetailsForDeletedFiles(self, owner, selectedFiles):
        """ This function is used to remove user access data for selected file from exposed users_access_data table"""

        pass

    def writeOrUpdateUserAccessData(self, accessRecord):
        """ This function is used to write or update  user access data for selected file from exposed users_access_data table"""
        pass

    def writeOrUpdateS3Data(self, s3Data):
        """ This function is used to put contents selected file from exposed Read server """
        pass

    def addUserAccessDetailsForFileorFolder(self, accessRecordsToBeInserted):
        """ This function is used to add user access detail for a particular user while uplading the file or folder in s3"""

        pass
