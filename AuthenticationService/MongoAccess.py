import configparser

from pymongo import MongoClient

""" This class is the core implementation of Mongo API"""

class MongoAccess:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mongo_database = config['MONGO']['DATABASE']
        self.client = MongoClient()
        self.database = self.client.get_database(name=mongo_database)

    def return_collection(self, collection_name):
        return self.database.get_collection(collection_name)

    def insert(self, record, collection):
        return collection.insert_one(record)

    def delete_one(self, filter, collection):
        return collection.delete_one(filter)

    def find_one(self, record, collection):
        return collection.find_one(record)
