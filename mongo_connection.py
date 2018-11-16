from pymongo import MongoClient

client = MongoClient()
database = client.authentication_db
collection = database.users_data




def insert(login_details):
    return collection.insert_one(login_details)
