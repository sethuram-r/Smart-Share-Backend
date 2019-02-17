import json
import re
import threading

from flask import request, jsonify

from Classes import MongoConnectionClassPool as mc, RedisConnectionClassPool as rc, AmazonS3ClassPool as s3


class ServiceClass:

    def __init__(self, request):
        self.request = request
        self.mongo_connection = mc.MongoConnectionClassPool().acquire()
        self.redis_connection = rc.RedisConnectionClassPool().acquire()
        self.s3_connection = s3.AmazonS3ClassPool().acquire()
        print("note", self.s3_connection)

    def __del__(self):
        mc.MongoConnectionClassPool().release(self.mongo_connection)
        rc.RedisConnectionClassPool().release(self.redis_connection)
        s3.AmazonS3ClassPool().release(self.s3_connection)

    def data_extraction(self, data):

        extracted_data = str(data).replace("b", "", 1).replace("'", "").strip()
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
        print(login_credentials)
        return login_credentials

    def update(self):
        login_credentials = self.data_extraction(self.request.data)
        filter = {"username": login_credentials["username"]}
        result = self.mongo_connection.update(filter, login_credentials)
        if (result.raw_result["updatedExisting"]):
            print("The User data is updated successfully.......")
            return jsonify({"status": True})
        else:
            print("The data updation resulted in failure.......")
            return jsonify({"status": False})

    def insert(self):
        login_credentials = self.data_extraction(request.data)
        result = self.mongo_connection.insert(login_credentials)
        if (result) != "":
            print("The User data is inserted successfully.......")
            return jsonify({"status": True})
        else:
            print("The data insertion resulted in failure.......")
            return jsonify({"status": False})

    def find_one(self):
        login_credentials = self.data_extraction(request.data)
        result = self.mongo_connection.find_one(login_credentials)
        if (result) != "":
            print("The User data is exists .......")
            return jsonify({"status": True})
        else:
            print("The data doesn't exists.......")
            return jsonify({"status": False})

    def validate_user(self):
        username = request.args.get('username')
        session_id = request.args.get('sessionid')
        result = self.mongo_connection.find_one({"username": username, "authentication_server_sessionId": session_id})
        if (result) != "":
            print("The User data exists .......")
            return jsonify({"status": True})
        else:
            print("The data doesn't exists.......")
            return jsonify({"status": False})

    def send_objects(self):
        print(self.request)
        username = self.request
        # print("note", self.s3_connection)
        # print("request",self.request)
        result = self.s3_connection.list_objects("file.server.1", username)
        return (result)

    def sign_out(self):
        username = request.args.get('username')
        result = self.mongo_connection.find_one({"username": username})
        del result["_id"]
        del result["authentication_server_sessionId"]
        replace_result = self.mongo_connection.replace({"username": username}, result)
        if replace_result.modified_count == 1:
            print("The User has been logged out .......")
            return jsonify({"status": True})
        else:
            print("The User has not been logged out.......")
            return jsonify({"status": False})

    def get_object(self, object=""):
        key = request.args.get('key')
        if object: key = object
        if self.redis_connection.exists("cache:" + key) == 1:
            data_from_cache = self.redis_connection.get_object("cache:" + key)
            print("returned from cache")
            return data_from_cache
        else:
            data_from_s3 = self.s3_connection.get_object("file.server.1", key)
            return data_from_s3

    def upload_object(self):
        print(request.data)
        data = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
        ownername = data["owner"]
        access_collection = self.mongo_connection.return_collection("users_access_data")
        files = data["data"]
        results = []
        folder_access = []

        def worker():
            print("worker started")
            access_collection.delete_many(folder_access)
            file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
            if files[0]["name"] == "":
                path = self.s3_connection.one_folder_up(files[0]["path"])
            else:
                path = files[0]["path"]
            objects = self.redis_connection.get_keys(pattern="backup:" + path + "*")
            files_from_backup = []
            for object in objects:
                object = str(object).replace("b", "", 1).replace("'", "").strip()
                backup_file = {}
                if file_extension.search(object):
                    backup_file["path"] = self.s3_connection.one_folder_up(object.replace("backup:", "").strip())
                    backup_file["name"] = list(filter(None, object.split("/")))[-1]
                    backup_file["file"] = self.redis_connection.get_object(object)
                else:
                    backup_file["path"] = object.replace("backup:", "").strip()
                    backup_file["name"] = ""
                    backup_file["file"] = ""

                files_from_backup.append(backup_file)
            for each_backup_file in files_from_backup:
                self.s3_connection.upload_object(each_backup_file)

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

            version_id = self.s3_connection.upload_object(file)
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

    def delete_objects(self):
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
            backup = self.mongo_connection.find_one(folder_access_temp,
                                                    self.mongo_connection.return_collection("users_access_data"))
            del backup["_id"]
            backups.append(backup)
            folder_access.append(folder_access_temp)

        print("backup", backups)
        self.mongo_connection.delete_many(folder_access, self.mongo_connection.return_collection("users_access_data"))
        results = []
        results.append(self.s3_connection.delete_objects(objects))
        print(results)

        def worker():
            access_collection = self.mongo_connection.return_collection("users_access_data")
            access_collection.insert_many(backups)

        if (False in results):
            print("inside rollback")
            try:
                delete_roll_back_thread = threading.Thread(target=worker())
                thread = threading.Thread(target=self.s3_connection.roll_back, args=(objects["Objects"],))
                thread.daemon = True
                delete_roll_back_thread.daemon = True
                delete_roll_back_thread.start()
                thread.start()
            except:
                print("Error: unable to Rollback")
            return jsonify({"status": False})
        else:
            return jsonify({"status": True})

    def lock_objects(self):
        objects = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
        results = []
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        lock = self.redis_connection.lock(objects["task"])
        for object in objects["data"]:
            content = ""
            if file_extension.search(object): content = self.get_object(object)
            # Creating and Deleting Savepoint
            savepoint, arg = self.redis_connection.savepoint(objects["task"], key=object, data=content)
            savepoint(**arg)
            results.append(lock(object))

        print(results)
        if (False in results):
            return jsonify({"status": False})
        else:
            return jsonify({"status": True})

    def lock_status(self):
        object = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
        if self.redis_connection.exists("lock:" + object["key"]):
            lock_status = self.redis_connection.lock_status(object["key"])
            print(lock_status)
        else:
            return jsonify({"status": True})
        if str(lock_status).replace("b", "", 1).replace("'", "") == "Yes":
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})

    def access_request(self):
        path = request.args.get('path')
        username = request.args.get('username')
        access = request.args.get('access')
        owner = request.args.get('owner')
        collection = self.mongo_connection.return_collection("user_access_request")
        parameter = {"file": path, "owner": owner, "username": username, "access": access, "status": "ongoing"}
        print("parameter", parameter)
        result = self.mongo_connection.insert(parameter, collection)
        print("result", result.inserted_id)
        if (result.inserted_id):
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})

    def requested_access(self):
        username = request.args.get('username')
        role = request.args.get('role')
        collection = self.mongo_connection.return_collection("user_access_request")
        filter = {role: username}
        # print(filter)
        return jsonify(self.mongo_connection.find(filter, collection))

    def request_status(self):
        object = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
        print(object)
        if object["status"] == "approve":
            del object["status"]
            access_collection = self.mongo_connection.return_collection("users_access_data")
            parameter_to_find = {"file": object["file"], "owner": object["owner"]}
            find_result = self.mongo_connection.find_one(parameter_to_find, access_collection)
            del find_result["_id"]
            replacing_result = self.s3_connection.create_replace_record(find_result, object)
            result = self.mongo_connection.replace(parameter_to_find, replacing_result, access_collection)
            print(result.modified_count)
            if result.modified_count == 1:
                collection = self.mongo_connection.return_collection("user_access_request")
                replace_result = self.s3_connection.status_change(collection, object, "approved")
                if replace_result.modified_count == 1:
                    return jsonify({"status": True})
                else:
                    return jsonify({"status": False})
        else:
            collection = self.mongo_connection.return_collection("user_access_request")
            replace_result = self.s3_connection.status_change(collection, object, "rejected")
            if replace_result.modified_count == 1:
                return jsonify({"status": True})
            else:
                return jsonify({"status": False})

    def delete_record(self):
        object = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
        collection = self.mongo_connection.return_collection("user_access_request")
        result = self.mongo_connection.delete_one(object, collection)
        if result.deleted_count == 1:
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})

    def accessed_records(self):
        username = request.args.get('username')
        access_collection = self.mongo_connection.return_collection("users_access_data")
        filter = {"owner": username}
        result = self.s3_connection.file_accesses_others(self.mongo_connection.find(filter, access_collection))
        print(result)
        return jsonify(result)
