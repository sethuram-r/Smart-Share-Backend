import configparser

from AuthenticationService import MongoReads

""" This class is a common interface which gives flexibility to change or add other databases in future."""


class DataBaseInterface:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.registered_users_collection = config['MONGO']['REGISTERED_USERS_COLLECTION']
        self.session_validation_collection = config['MONGO']['SESSION_VALIDATION_COLLECTION']

    def findSignInRecordInDatabase(self, record):
        """ This is used to access the database (MongoDB) to find one single sign in  record """
        doesRecordExists = MongoReads.MongoReads.findOneRecord(record, self.registered_users_collection)
        return doesRecordExists

    def findSessionRecordInDatabase(self, record):
        """ This is used to access the database (MongoDB) to find one single session record """
        doesRecordExists = MongoReads.MongoReads.findOneRecord(record, self.session_validation_collection)
        return doesRecordExists
