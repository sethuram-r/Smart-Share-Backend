import configparser
from json import loads

from kafka import KafkaConsumer

from AuthenticationService import MongoAccess, logging


class AuthenticationConsumer:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('AuthenticationConfig.ini')
        self.sign_up = config['TASKS']['SIGN_UP']
        self.sign_in = config['TASKS']['SIGN_IN']
        self.log_out = config['TASKS']['LOG_OUT']
        self.registered_users_collection = config['MONGO']['REGISTERED_USERS_COLLECTION']
        self.session_validation_collection = config['MONGO']['SESSION_VALIDATION_COLLECTION']
        self.mongo_connection = MongoAccess.MongoAccess()
        self.consumer()

    def keyDeserializer(self, key):
        return key.decode('utf-8')

    def valueDeserializer(self, value):
        return loads(value.decode('utf-8'))

    def signUp(self, signup_requests):

        logging.info("Consumer: Inside signUp")

        collection = self.mongo_connection.return_collection(self.registered_users_collection)
        insertion_result = self.mongo_connection.insert(signup_requests, collection)
        if insertion_result.acknowledged == False:
            logging.critical("Error in Insertion during SignUp %s", signup_requests)

    def createSearchRecordForReplace(self, record):
        searchRecord = {}
        if "username" in record: searchRecord["username"] = record["username"]
        return searchRecord


    def signIn(self, session_records):

        logging.info("Consumer: Inside signIn")

        collection = self.mongo_connection.return_collection(self.session_validation_collection)
        insertion_result = self.mongo_connection.replace(
            recordToReplace=self.createSearchRecordForReplace(session_records),
            replacementRecord=session_records, collection=collection)
        if insertion_result.acknowledged == False:
            logging.critical("Error in Insertion during SignIn %s", session_records)

    def logOut(self, logout_records):

        logging.info("Consumer: Inside logOut")

        collection = self.mongo_connection.return_collection(self.session_validation_collection)
        deletion_result = self.mongo_connection.delete_one(logout_records, collection)
        if deletion_result.deleted_count != 1:
            logging.critical("Error in Deletion during logOut %s", logout_records)


    def consumer(self):

        consumer = KafkaConsumer(
            'authentication',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='authentication-group'

        )
        for requests_or_records in consumer:

            if self.keyDeserializer(requests_or_records.key) == self.sign_up: self.signUp(
                self.valueDeserializer(requests_or_records.value))
            if self.keyDeserializer(requests_or_records.key) == self.sign_in: self.signIn(
                self.valueDeserializer(requests_or_records.value))
            if self.keyDeserializer(requests_or_records.key) == self.log_out: self.logOut(
                self.valueDeserializer(requests_or_records.value))


AuthenticationConsumer()
