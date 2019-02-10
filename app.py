import json
import re
import threading

from flask import Flask, request, jsonify

import amazon_s3_connection as s3
import mongo_connection as mc
import redis_connection as rc

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024


def data_extraction(data):

    extracted_data = str(data).replace("b","",1).replace("'","").strip()
    # print(extracted_data)
    login_credentials = {}
    if (extracted_data.split(",")[0].split(":")[0] == "user_name"):
         login_credentials["username"] = extracted_data.split(",")[0].split(":")[1]
    if (extracted_data.split(",")[1].split(":")[0] == "password"):
         login_credentials["password"] = extracted_data.split(",")[1].split(":")[1]
    if (extracted_data.split(",")[1].split(":")[0] == "sessionId"):
         login_credentials["authentication_server_sessionId"] = extracted_data.split(",")[1].split(":")[1]
    if (extracted_data.split(",")[0].split(":")[0] == "file"):
        login_credentials["file"] = extracted_data.split(",")[0].split(":")[1]
    # if (extracted_data.split(",")[1].split(":")[0] == "name"):
    #     login_credentials["file_name"] = extracted_data.split(",")[0].split(":")[1]
    print(login_credentials)
    return login_credentials


@app.route('/register',methods=['POST'])
def update():
    login_credentials = data_extraction(request.data)
    filter = {"username": login_credentials["username"]}
    result = mc.update(filter,login_credentials)
    if (result.raw_result["updatedExisting"]):
        print("The User data is updated successfully.......")
        return jsonify({"status": True})
    else:
        print("The data updation resulted in failure.......")
        return jsonify({"status": False})


@app.route('/signup',methods=['POST'])
def insert():
     login_credentials =  data_extraction(request.data)
     result = mc.insert(login_credentials)
     if (result) != "":
         print("The User data is inserted successfully.......")
         return  jsonify({"status":True})
     else:
         print("The data insertion resulted in failure.......")
         return jsonify({"status":False})

   
@app.route('/signin', methods=['POST'])
def find_one():
    login_credentials = data_extraction(request.data)
    result = mc.find_one(login_credentials)
    if (result) != "":
         print("The User data is exists .......")
         return  jsonify({"status":True})
    else:
         print("The data doesn't exists.......")
         return jsonify({"status":False})


@app.route('/validateSession', methods=['GET'])
def validate_user():
    username = request.args.get('username')
    session_id = request.args.get('sessionid')
    result = mc.find_one({"username": username, "authentication_server_sessionId": session_id})
    if (result) != "":
        print("The User data exists .......")
         return  jsonify({"status":True})
    else:
         print("The data doesn't exists.......")
         return jsonify({"status":False})


@app.route('/getObjects', methods=['GET'])
def send_objects():
    username = request.args.get('username')
    return jsonify(s3.list_objects("file.server.1", username))


@app.route('/logout', methods=['GET'])
def sign_out():
    username = request.args.get('username')
    result = mc.find_one({"username": username})
    del result["_id"]
    del result["authentication_server_sessionId"]
    replace_result = mc.replace({"username": username}, result)
    if replace_result.modified_count == 1:
        print("The User has been logged out .......")
        return jsonify({"status": True})
    else:
        print("The User has not been logged out.......")
        return jsonify({"status": False})




@app.route('/getObject', methods=['GET'])
def get_object(object=""):
    key = request.args.get('key')
    if object: key = object
    if rc.exists("cache:" + key) == 1:
        data_from_cache = rc.get_object("cache:" + key)
        print("returned from cache")
        return data_from_cache
    else:
        data_from_s3 = s3.get_object("file.server.1", key)
        return data_from_s3


@app.route('/uploadObject', methods=['POST'])
def upload_object():
    print(request.data)
    data = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    ownername = data["owner"]
    access_collection = mc.return_collection("users_access_data")
    files = data["data"]
    results = []
    folder_access = []

    def worker():
        print("worker started")
        access_collection.delete_many(folder_access)
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        if files[0]["name"] == "":
            path = s3.one_folder_up(files[0]["path"])
        else:
            path = files[0]["path"]
        objects = rc.get_keys(pattern="backup:" + path + "*")
        files_from_backup = []
        for object in objects:
            object = str(object).replace("b", "", 1).replace("'", "").strip()
            backup_file = {}
            if file_extension.search(object):
                backup_file["path"] = s3.one_folder_up(object.replace("backup:", "").strip())
                backup_file["name"] = list(filter(None, object.split("/")))[-1]
                backup_file["file"] = rc.get_object(object)
            else:
                backup_file["path"] = object.replace("backup:", "").strip()
                backup_file["name"] = ""
                backup_file["file"] = ""

            files_from_backup.append(backup_file)
        for each_backup_file in files_from_backup:
            s3.upload_object(each_backup_file)


    for file in files:
        folder_access_temp = {}
        folder_access_temp["owner"] = ownername
        folder_access_temp["file"] = file["path"] + file["name"]
        users_accessing_object = []
        user_accessing_object = {}
        user_accessing_object["name"] = ownername
        user_accessing_object["read"] = True
        user_accessing_object["write"] = True
        user_accessing_object["delete"] = True
        users_accessing_object.append(user_accessing_object)
        folder_access_temp["accessing_users"] = users_accessing_object
        folder_access.append(folder_access_temp)

        version_id = s3.upload_object(file)
        if (version_id):
            results.append(True)

    print(results)
    print(folder_access)
    access_collection.insert_many(folder_access)
    if (False in results):
        print("inside rollback")
        try:
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
        except:
            print("Error: unable to Rollback")
        return jsonify({"status": False})
    else:
        return jsonify({"status": True})



@app.route('/deleteObjects', methods=['POST'])
def delete_objects():
    objects = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    data = objects["Objects"]
    username = objects["owner"]
    del objects["owner"]
    folder_access = []
    backups = []

    for file in data:
        folder_access_temp = {}
        folder_access_temp["owner"] = username
        folder_access_temp["file"] = file["Key"]
        backup = mc.find_one(folder_access_temp, mc.return_collection("users_access_data"))
        del backup["_id"]
        backups.append(backup)
        folder_access.append(folder_access_temp)

    print("backup", backups)
    mc.delete_many(folder_access, mc.return_collection("users_access_data"))
    results = []
    results.append(s3.delete_objects(objects))
    print(results)

    def worker():
        access_collection = mc.return_collection("users_access_data")
        access_collection.insert_many(backups)

    if (False in results):
        print("inside rollback")
        try:
            delete_roll_back_thread = threading.Thread(target=worker())
            thread = threading.Thread(target=s3.roll_back, args=(objects["Objects"],))
            thread.daemon = True
            delete_roll_back_thread.daemon = True
            delete_roll_back_thread.start()
            thread.start()
        except:
            print("Error: unable to Rollback")
        return jsonify({"status": False})
    else:
        return jsonify({"status": True})


@app.route('/lockObjects', methods=['POST'])
def lock_objects():
    objects = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    results = []
    file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
    lock = rc.lock(objects["task"])
    for object in objects["data"]:
        content = ""
        if file_extension.search(object): content = get_object(object)
        # Creating and Deleting Savepoint
        savepoint, arg = rc.savepoint(objects["task"], key=object, data=content)
        savepoint(**arg)
        results.append(lock(object))

    print(results)
    if (False in results):
        return jsonify({"status": False})
    else:
        return jsonify({"status": True})


@app.route('/lockStatus', methods=['POST'])
def lock_status():
    object = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    if rc.exists("lock:" + object["key"]):
        lock_status = rc.lock_status(object["key"])
        print(lock_status)
    else:
        return jsonify({"status": True})
    if str(lock_status).replace("b", "", 1).replace("'", "") == "Yes":
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})


@app.route('/accessRequest', methods=['Get'])
def access_request():
    path = request.args.get('path')
    username = request.args.get('username')
    access = request.args.get('access')
    owner = request.args.get('owner')
    collection = mc.return_collection("user_access_request")
    parameter = {"file": path, "owner": owner, "username": username, "access": access, "status": "ongoing"}
    print("parameter", parameter)
    result = mc.insert(parameter, collection)
    print("result", result.inserted_id)
    if (result.inserted_id):
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})


@app.route('/getAccessRequests', methods=['Get'])
def requested_access():
    username = request.args.get('username')
    role = request.args.get('role')
    collection = mc.return_collection("user_access_request")
    filter = {role: username}
    # print(filter)
    return jsonify(mc.find(filter, collection))


@app.route('/requestStatus', methods=['POST'])
def request_status():
    object = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    print(object)
    if object["status"] == "approve":
        del object["status"]
        access_collection = mc.return_collection("users_access_data")
        parameter_to_find = {"file": object["file"], "owner": object["owner"]}
        find_result = mc.find_one(parameter_to_find, access_collection)
        del find_result["_id"]
        replacing_result = s3.create_replace_record(find_result, object)
        result = mc.replace(parameter_to_find, replacing_result, access_collection)
        print(result.modified_count)
        if result.modified_count == 1:
            collection = mc.return_collection("user_access_request")
            replace_result = s3.status_change(collection, object, "approved")
            if replace_result.modified_count == 1:
                return jsonify({"status": True})
            else:
                return jsonify({"status": False})
    else:
        collection = mc.return_collection("user_access_request")
        replace_result = s3.status_change(collection, object, "rejected")
        if replace_result.modified_count == 1:
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})


@app.route('/deleteRecord', methods=['POST'])
def delete_record():
    object = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    collection = mc.return_collection("user_access_request")
    result = mc.delete_one(object, collection)
    if result.deleted_count == 1:
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})


@app.route('/getAccessedRecords', methods=['Get'])
def accessed_records():
    username = request.args.get('username')
    access_collection = mc.return_collection("users_access_data")
    filter = {"owner": username}
    result = s3.file_accesses_others(mc.find(filter, access_collection))
    print(result)
    return jsonify(result)



if __name__ == '__main__':
    app.run()

