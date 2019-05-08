import configparser
from json import loads

from kafka import KafkaConsumer

from AuthenticationService import MongoAccess, logging


class MongoWrites:

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

    def signUp(self, signup_requests):

        logging.info("Inside MongoWrites.signUp")

        collection = self.mongo_connection.return_collection(self.registered_users_collection)
        insertion_result = self.mongo_connection.insert(signup_requests, collection)
        if insertion_result.acknowledged == False:
            logging.critical("Error in Insertion %s", signup_requests)

    def signIn(self, session_records):

        logging.info("Inside MongoWrites.signIn")

        collection = self.mongo_connection.return_collection(self.session_validation_collection)
        insertion_result = self.mongo_connection.insert(session_records, collection)
        if insertion_result.acknowledged == False:
            logging.critical("Error in Insertion %s", session_records)


    def logOut(self, logout_records):

        logging.info("Inside MongoWrites.logOut")

        collection = self.mongo_connection.return_collection(self.session_validation_collection)
        deletion_result = self.mongo_connection.delete_one(logout_records, collection)
        if deletion_result.deleted_count != 1:
            logging.critical("Error in Deletion %s", logout_records)


    ## General Note:
    """ Multiple signin by single user is possible. But due to this there will be huge dump of session info in db. 
    Therefore a function can be triggered in db to delete the records in sesseion table per day basis. """

    def consumer(self):

        consumer = KafkaConsumer(
            'authentication',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='authentication-group',
            key_deserializer=lambda x: (x.decode('utf-8')),
            value_deserializer=lambda x: loads(x.decode('utf-8')))

        for requests_or_records in consumer:

            if requests_or_records.key == self.sign_up: self.signUp(requests_or_records.value)
            if requests_or_records.key == self.sign_in: self.signIn(requests_or_records.value)
            if requests_or_records.key == self.log_out: self.logOut(requests_or_records.value)


MongoWrites()
