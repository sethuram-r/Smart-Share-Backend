from pymongo import MongoClient

client = MongoClient()
database = client.authentication_db
collection = database.users_data


def insert(login_details):
    return collection.insert_one(login_details)



def find_one(login_details):
    return collection.find_one(login_details)


def update(filter,update_details):
    return collection.update_one(filter,{ "$set": update_details })