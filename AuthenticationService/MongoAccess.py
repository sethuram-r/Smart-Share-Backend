import configparser

from pymongo import MongoClient


class MongoAccess:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mongo_database = config['MONGO']['DATABASE']
        registered_users_colleaction = config['MONGO']['REGISTERED_USERS_COLLECTION']
        self.client = MongoClient()
        self.database = self.client.get_database(name=mongo_database)
        self.collection = self.database.get_collection(name=registered_users_colleaction)

    def return_collection(self, collection_name):
        return self.database.get_collection(collection_name)

    def insert(self, record, collection):
        return collection.insert_one(record)

    def delete_one(self, filter, collection):
        return collection.delete_one(filter)
