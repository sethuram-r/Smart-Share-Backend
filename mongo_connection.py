from pymongo import MongoClient

client = MongoClient()
database = client.authentication_db
collection = database.users_data



def insert(login_details):
    result = collection.insert_one(login_details).inserted_id

    if (result) != "":
        print("The User data is inserted successfully.......")
        return True
    else:
        print("The data insertion resulted in failure.......")
        return False
