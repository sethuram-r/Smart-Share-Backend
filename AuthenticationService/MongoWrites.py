import configparser
from json import loads

from kafka import KafkaConsumer

from AuthenticationService import MongoAccess


class MongoWrites:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.sign_up = config['TASKS']['SIGN_UP']
        self.sign_in = config['TASKS']['SIGN_IN']
        self.log_out = config['TASKS']['LOG_OUT']
        self.registered_users_collection = config['MONGO']['REGISTERED_USERS_COLLECTION']
        self.session_validation_collection = config['MONGO']['SESSION_VALIDATION_COLLECTION']
        self.mongo_connection = MongoAccess.MongoAccess()
        self.consumer()

    def signUp(self, signup_requests):

        """ Function to insert the user registration details into DB """

        collection = self.mongo_connection.return_collection(self.registered_users_collection)
        insertion_result = self.mongo_connection.insert(signup_requests, collection)
        if insertion_result.acknowledged == False: print(
            "{}------{}----{}".format('Warning', signup_requests, 'Error in Insertion'))  # logger implementation

    def signIn(self, session_records):

        """ Function to insert the session key into DB
        which is obtained from processing the sigin request that is consumed through streams """

        collection = self.mongo_connection.return_collection(self.session_validation_collection)
        insertion_result = self.mongo_connection.insert(session_records, collection)
        if insertion_result.acknowledged == False: print(
            "{}------{}----{}".format('Warning', session_records, 'Error in Insertion'))  # logger implementation

    def logOut(self, logout_records):

        """ Function to delete the session key in DB
        which is obtained from processing the logout request that is consumed through streams """

        collection = self.mongo_connection.return_collection(self.session_validation_collection)
        deletion_result = self.mongo_connection.delete_one(logout_records, collection)
        if deletion_result.deleted_count != 1: print(
            "{}------{}----{}".format('Warning', logout_records, 'Error in Deletion'))  # logger implementation

    ## General Note:
    """ Multiple signin by single user is possible. But due to this there will be huge dump of session info in db. 
    Therefore a function can be triggered in db to delete the records in sesseion table per day basis. """

    def consumer(self):

        """ This is a kafka consumer that consumes the events and sends to the corresponding event handlers"""

        consumer = KafkaConsumer(
            'authentication',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='authentication-group',
            key_deserializer=lambda x: (x.decode('utf-8')),
            value_deserializer=lambda x: loads(x.decode('utf-8')))
        for requests_or_records in consumer:
            print("requests_or_records----------->", requests_or_records.value)

            """ Based on the key the events are filtered and processed.
             This would have been done by forming a new stream through stream processing using faust"""

            if requests_or_records.key == self.sign_up: self.signUp(requests_or_records.value)
            if requests_or_records.key == self.sign_in: self.signIn(requests_or_records.value)
            if requests_or_records.key == self.log_out: self.logOut(requests_or_records.value)
