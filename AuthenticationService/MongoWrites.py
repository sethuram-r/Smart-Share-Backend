import configparser
from json import loads

from kafka import KafkaConsumer

from AuthenticationService import MongoAccess


class MongoWrites:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.sign_up = config['TASKS']['SIGN_UP']
        self.registered_users_collection = config['MONGO']['REGISTERED_USERS_COLLECTION']
        self.mongo_connection = MongoAccess.MongoAccess()
        self.consumer()

    def signUp(self, signup_requests):
        collection = self.mongo_connection.return_collection(self.registered_users_collection)
        insertion_result = self.mongo_connection.insert(signup_requests, collection)
        if insertion_result.acknowledged == False: print(
            "{}------{}----{}".format('Warning', signup_requests, 'Error in Insertion'))

    def consumer(self):
        consumer = KafkaConsumer(
            'authentication',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='authentication-group',
            key_deserializer=lambda x: (x.decode('utf-8')),
            value_deserializer=lambda x: loads(x.decode('utf-8')))
        for signup_requests in consumer:
            print("signup_requests----------->", signup_requests.value)
            if signup_requests.key == self.sign_up: self.signUp(signup_requests.value)
