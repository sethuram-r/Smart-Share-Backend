import configparser

from AuthenticationService import MongoReads, logging

""" This class is a common interface which gives flexibility to change or add other databases in future."""


class DataBaseInterface:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('AuthenticationConfig.ini')
        self.registered_users_collection = config['MONGO']['REGISTERED_USERS_COLLECTION']
        self.session_validation_collection = config['MONGO']['SESSION_VALIDATION_COLLECTION']

    def findSignInRecordInDatabase(self, record):
        logging.info("Inside findSignInRecordInDatabase ")

        doesRecordExists = MongoReads.MongoReads().findOneRecord(record, self.registered_users_collection)
        logging.debug("Does Record Exists %s", doesRecordExists)
        return doesRecordExists

    def findSessionRecordInDatabase(self, record):
        logging.info("Inside findSessionRecordInDatabase ")

        doesRecordExists = MongoReads.MongoReads().findOneRecord(record, self.session_validation_collection)
        logging.debug("Does Record Exists %s", doesRecordExists)
        return doesRecordExists
