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

@app.route('/validate', methods=['POST'])
def validate_user():
    credentials = data_extraction(request.data)
    result = mc.find_one(credentials)
    print(credentials)
    if (result) != "":
         print("The User data is exists .......")
         return  jsonify({"status":True})
    else:
         print("The data doesn't exists.......")
         return jsonify({"status":False})


@app.route('/getObjects', methods=['GET'])
def send_objects():
    return jsonify(s3.list_objects("file.server.1"))


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
    files = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    results = []

    def worker():
        print("worker started")
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
        version_id = s3.upload_object(file)
        if (version_id): results.append(True)

    print(results)
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
    results = []
    results.append(s3.delete_objects(objects))
    print(results)
    if (False in results):
        print("inside rollback")
        try:
            thread = threading.Thread(target=s3.roll_back, args=(objects["Objects"],))
            thread.daemon = True
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
        lock_status = rc.loack_status(object["key"])
        print(lock_status)
    else:
        return jsonify({"status": True})
    if str(lock_status).replace("b", "", 1).replace("'", "") == "Yes":
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})



if __name__ == '__main__':
    app.run()

