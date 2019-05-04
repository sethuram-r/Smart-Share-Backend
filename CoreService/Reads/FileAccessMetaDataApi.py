import configparser


class FileAccessMetaDataApi:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('CoreConfig.ini')
        self.__accessDataUrl = config['URL']['ACCESS_DATA_INFO_URL']
        self.__defaultTopicName = config['HELPERS']['DEFAULT_TOPIC_NAME']

    def fetchUserAcessDataForFilesandFolders(self):
        return None  # have to remove once access management is done

        # response = requests.get(url=self.__accessDataUrl)
        # print("response------------------>", response)
        #
        # return response
