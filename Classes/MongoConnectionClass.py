import configparser

from pymongo import MongoClient


class MongoConnectionClass:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        mongo_database = config['MONGO']['DATABASE']
        users_data_colleaction = config['MONGO']['USER_DATA_COLLECTION']
        self.client = MongoClient()
        self.database = self.client.get_database(name=mongo_database)
        self.collection = self.database.get_collection(name=users_data_colleaction)

    def return_collection(self, collection_name):
        return self.database.get_collection(collection_name)

    def insert(self, login_details, collection=""):
        if collection == "": collection = self.collection
        return collection.insert_one(login_details)

    def find_one(self, login_details, collection=""):
        if collection == "": collection = self.collection
        return collection.find_one(login_details)

    def update(self, filter, update_details, collection=""):
        if collection == "": collection = self.collection
        return collection.update_one(filter, {"$set": update_details})

    def insert_many(self, data):
        return self.collection.insert_many(data)

    def delete_many(self, data, collection=""):
        results = []
        if collection == "": collection = self.collection
        for each in data:
            result = collection.delete_one(each)
            results.append(result.deleted_count)
        print(results)
        return results

    def find(filter, collection):
        results = []
        for grid_data in collection.find(filter, no_cursor_timeout=True):
            del grid_data['_id']
            results.append(grid_data)
        return results

    def replace(self, filter, record_to_be_replaced, collection=""):
        if collection == "": collection = self.collection
        return collection.replace_one(filter, record_to_be_replaced)

    def delete_one(self, filter, collection=""):
        if collection == "": collection = self.collection
        return collection.delete_one(filter)
