import re
import re
import threading

from Classes import AmazonS3Class


# from flask import request


class ServiceClass(AmazonS3Class.AmazonS3Class):

    def __init__(self, request):
        print("The ServiceClass constructor invoked...........")
        self.request = request
        AmazonS3Class.AmazonS3Class.__init__(self)

    def register(self):
        login_credentials = self.request["data"]
        filter = {"username": login_credentials["username"]}
        result = self.mongo_connection.update(filter, login_credentials)
        if (result.raw_result["updatedExisting"]):
            print("The User data is updated successfully.......")
            return ({"status": True})
        else:
            print("The data updation resulted in failure.......")
            return ({"status": False})

    def signUp(self):
        result = self.mongo_connection.insert(self.request["data"])
        del self.request["data"]["_id"]
        if result.acknowledged == True:
            print("The User data is inserted successfully.......")
            return {"status": True}
        else:
            print("The data insertion resulted in failure.......")
            return ({"status": False})

    def signIn(self):

        login_credentials = self.request["data"]
        result = self.mongo_connection.find_one(login_credentials)
        if (result) != "":
            print("The User data is exists .......")
            return ({"status": True})
        else:
            print("The data doesn't exists.......")
            return ({"status": False})

    def validateSession(self):
        username = self.request.get('username')
        session_id = self.request.get('sessionid')
        result = self.mongo_connection.find_one({"username": username, "authentication_server_sessionId": session_id})
        if (result) != "":
            print("The User data exists .......")
            return {"status": True}
        else:
            print("The data doesn't exists.......")
            return {"status": False}

    def getObjects(self):
        username = self.request["param"].get('username')
        return self.list_objects("file.server.1", username)

    def logOut(self):
        username = self.request["param"].get('username')
        result = self.mongo_connection.find_one({"username": username})

        del result["_id"]
        del result["sessionId"]
        replace_result = self.mongo_connection.replace({"username": username}, result)
        if replace_result.modified_count == 1:
            print("The User has been logged out .......")
            return ({"status": True})
        else:
            print("The User has not been logged out.......")
            return ({"status": False})

    def getObject(self, object=""):
        key = object if object else self.request["param"].get('key')
        if self.redis_connection.exists("cache:" + key) == 1:
            data_from_cache = self.redis_connection.get_object("cache:" + key)
            print("returned from cache")
            return data_from_cache
        else:
            data_from_s3 = self.get_object("file.server.1", key)
            print("returned from s3")
            return data_from_s3

    def uploadObject(self):
        print("inside uploadObject")
        data = self.request["data"]
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
                path = self.one_folder_up(files[0]["path"])
            else:
                path = files[0]["path"]
            objects = self.redis_connection.get_keys(pattern="backup:" + path + "*")
            files_from_backup = []
            for object in objects:
                object = str(object).replace("b", "", 1).replace("'", "").strip()
                backup_file = {}
                if file_extension.search(object):
                    backup_file["path"] = self.one_folder_up(object.replace("backup:", "").strip())
                    backup_file["name"] = list(filter(None, object.split("/")))[-1]
                    backup_file["file"] = self.redis_connection.get_object(object)
                else:
                    backup_file["path"] = object.replace("backup:", "").strip()
                    backup_file["name"] = ""
                    backup_file["file"] = ""

                files_from_backup.append(backup_file)
            for each_backup_file in files_from_backup:
                self.upload_object(each_backup_file)

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
            print("about to upload")
            version_id = self.upload_object(file)
            print("version_id-------", version_id)
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
            return ({"status": False})
        else:
            return ({"status": True})

    def deleteObjects(self):
        objects = self.request["data"]
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
        results.append(self.delete_objects(objects))
        print(results)

        def worker():
            access_collection = self.mongo_connection.return_collection("users_access_data")
            access_collection.insert_many(backups)

        if (False in results):
            print("inside rollback")
            try:
                delete_roll_back_thread = threading.Thread(target=worker())
                thread = threading.Thread(target=self.roll_back, args=(objects["Objects"],))
                thread.daemon = True
                delete_roll_back_thread.daemon = True
                delete_roll_back_thread.start()
                thread.start()
            except:
                print("Error: unable to Rollback")
            return ({"status": False})
        else:
            return ({"status": True})

    def lockObjects(self):
        objects = self.request["data"]
        results = []
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        lock = self.redis_connection.lock(objects["task"])
        for object in objects["data"]:
            content = ""
            if file_extension.search(object): content = self.getObject(object)
            # Creating and Deleting Savepoint
            savepoint, arg = self.redis_connection.savepoint(objects["task"], key=object, data=content)
            savepoint(**arg)
            results.append(lock(object))

        print(results)
        if (False in results):
            return ({"status": False})
        else:
            return ({"status": True})

    def lockStatus(self):
        object = self.request["data"]
        if self.redis_connection.exists("lock:" + object["key"]):
            lock_status = self.redis_connection.lock_status(object["key"])
            print(lock_status)
        else:
            return ({"status": True})
        if str(lock_status).replace("b", "", 1).replace("'", "") == "Yes":
            return ({"status": True})
        else:
            return ({"status": False})

    def accessRequest(self):
        path = self.request["param"].get('path')
        username = self.request["param"].get('username')
        access = self.request["param"].get('access')
        owner = self.request["param"].get('owner')
        collection = self.mongo_connection.return_collection("user_access_request")
        parameter = {"file": path, "owner": owner, "username": username, "access": access, "status": "ongoing"}
        print("parameter", parameter)
        result = self.mongo_connection.insert(parameter, collection)
        print("result", result.inserted_id)
        if (result.inserted_id):
            return ({"status": True})
        else:
            return ({"status": False})

    def requestStatus(self):
        object = self.request["data"]
        print(object)
        if object["status"] == "approve":
            del object["status"]
            access_collection = self.mongo_connection.return_collection("users_access_data")
            parameter_to_find = {"file": object["file"], "owner": object["owner"]}
            find_result = self.mongo_connection.find_one(parameter_to_find, access_collection)
            del find_result["_id"]
            replacing_result = self.create_replace_record(find_result, object)
            result = self.mongo_connection.replace(parameter_to_find, replacing_result, access_collection)
            print(result.modified_count)
            if result.modified_count == 1:
                collection = self.mongo_connection.return_collection("user_access_request")
                replace_result = self.status_change(collection, object, "approved")
                if replace_result.modified_count == 1:
                    return ({"status": True})
                else:
                    return ({"status": False})
        else:
            collection = self.mongo_connection.return_collection("user_access_request")
            replace_result = self.status_change(collection, object, "rejected")
            if replace_result.modified_count == 1:
                return ({"status": True})
            else:
                return ({"status": False})

    def deleteRecord(self):
        object = self.request["data"]
        collection = self.mongo_connection.return_collection("user_access_request")
        result = self.mongo_connection.delete_one(object, collection)
        if result.deleted_count == 1:
            return ({"status": True})
        else:
            return ({"status": False})

    def getAccessedRecords(self):

        """ This function is used to get the user's records accessed by others"""

        username = self.request["param"].get('username')
        access_collection = self.mongo_connection.return_collection("users_access_data")
        # filter = {"accessing_users": {"$elemMatch": {"name": username}}}
        filter = {"accessing_users.name": username}
        records_accessed_by_users = self.mongo_connection.find(filter, access_collection)
        print("records_accessed_by_users--------->", records_accessed_by_users)
        result = self.file_accesses_others(records_accessed_by_users, username)
        return (result)

    def getAccessRequests(self):

        """ This function is used to get the access request sent by the user to the owners of the respective folders"""

        username = self.request["param"].get('username')
        collection = self.mongo_connection.return_collection("user_access_request")
        filter = {"username": username}
        result = self.mongo_connection.find(filter, collection)
        return (result)

    def getAccessWaitingForApprovals(self):

        """ This function is used to get the access request waiting for approval for the folder owners"""

        owner = self.request["param"].get('owner')
        collection = self.mongo_connection.return_collection("user_access_request")
        filter = {"owner": owner}
        result = self.mongo_connection.find(filter, collection)
        return (result)
