from pymongo import MongoClient

client = MongoClient()
database = client.authentication_db
collection = database.users_data


def return_collection(collection_name):
    return database.get_collection(collection_name)


def insert(login_details, collection=""):
    if collection == "": collection = database.users_data
    return collection.insert_one(login_details)


def find_one(login_details, collection=""):
    if collection == "": collection = database.users_data
    return collection.find_one(login_details)


def update(filter, update_details, collection=""):
    if collection == "": collection = database.users_data
    return collection.update_one(filter,{ "$set": update_details })


def insert_many(data):
    return collection.insert_many(data)


def delete_many(data, collection=""):
    results = []
    if collection == "": collection = database.users_data
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


def replace(filter, record_to_be_replaced, collection=""):
    if collection == "": collection = database.users_data
    return collection.replace_one(filter, record_to_be_replaced)


def delete_one(filter, collection=""):
    if collection == "": collection = database.users_data
    return collection.delete_one(filter)
