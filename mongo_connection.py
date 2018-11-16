from pymongo import MongoClient

client = MongoClient()
database = client.authentication_db
collection = database.users_data



#localhost:27017



def insert(login_details):
    result = collection.insert_one(login_details).inserted_id

    if (result) != "":
        print("The User data is inserted successfully.......")
        return True
    else:
        print("The data insertion resulted in failure.......")
        return False


test = insert({"username": "banu", "password": "Sethu@143"})