import configparser
import pprint as pp
import threading

import boto3

from Classes import MongoConnectionClassPool as mc, RedisConnectionClassPool as rc


class AmazonS3Class:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        aws_access_key_id = config['DEFAULT']['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = config['DEFAULT']['AWS_SECRET_ACCESS_KEY']
        region_name = config['DEFAULT']['AWS_REGION_NAME']
        self.bucket_name = config['DEFAULT']['BUCKET_NAME']

        print("aws_access_key_id------------>", aws_access_key_id)

        self.client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name=region_name)
        self.mongo_connection = mc.MongoConnectionClassPool().acquire()
        # self.mongo_connection = MongoConnectionClass()
        # self.redis_connection = RedisConnectionClass()
        self.redis_connection = rc.RedisConnectionClassPool().acquire()

    def __del__(self):
        mc.MongoConnectionClassPool().release(self.mongo_connection)
        rc.RedisConnectionClassPool().release(self.redis_connection)

    def data_structure_transformer(self, value, username):
        import pprint as pp
        import re

        rjson = {}
        rjson["name"] = value["bucketName"]
        rjson["children"] = []
        file_extension_regex = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\....)$")

        def leaf_assignemnt(object):
            temp = object["objectName"].split("/")
            del temp[-1]
            root_folder_name = "/".join(temp) + "/"
            temp = {}
            temp["name"] = object["objectName"].replace(root_folder_name, "").strip()
            temp["trueName"] = object["objectName"]
            temp["value"] = round(object["size"] / 1024, 2)
            collection = self.mongo_connection.return_collection("users_access_data")
            parameter = {"file": object["objectName"]}
            metadata = self.mongo_connection.find_one(parameter, collection)
            if (metadata):
                temp["owner"] = metadata["owner"]
                for user in metadata["accessing_users"]:
                    if (user["name"] == username):
                        if "read" in user: temp["read"] = user["read"]
                        if "write" in user: temp["write"] = user["write"]
                        if "delete" in user: temp["delete"] = user["delete"]
            return temp

        def path_finder(start_position, folder):
            if start_position["children"] == []:
                return start_position
            else:
                for a in start_position["children"]:
                    if a["name"] == folder:
                        return a
                return start_position

        def branch_assignment(original_name, name):
            temp = {}
            temp["name"] = name
            temp["trueName"] = original_name
            temp["children"] = []
            collection = self.mongo_connection.return_collection("users_access_data")
            parameter = {"file": temp["trueName"]}
            metadata = self.mongo_connection.find_one(parameter, collection)
            if (metadata):
                temp["owner"] = metadata["owner"]
                for user in metadata["accessing_users"]:
                    if (user["name"] == username):
                        if "read" in user: temp["read"] = user["read"]
                        if "write" in user: temp["write"] = user["write"]
                        if "delete" in user: temp["delete"] = user["delete"]
            return temp

        def longestSubstringFinder(string1, string2):
            answer = ""
            len1, len2 = len(string1), len(string2)
            for i in range(len1):
                match = ""
                for j in range(len2):
                    if (i + j < len1 and string1[i + j] == string2[j]):
                        match += string2[j]
                    else:
                        if (len(match) > len(answer)): answer = match
                        match = ""
            return answer

        start_position = rjson
        previous_split = ""
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        for i in value["bucketData"]:
            if file_extension_regex.search(i["objectName"]) and "/" not in i["objectName"]:
                rjson["children"].append(leaf_assignemnt(i))
            elif i["objectName"].endswith('/') or file_extension.search(i["objectName"]):
                if file_extension.search(i["objectName"]):
                    splitted_root = list(filter(None, i["objectName"].split("/")))
                    del splitted_root[-1]
                else:
                    splitted_root = list(filter(None, i["objectName"].split("/")))
                if previous_split not in splitted_root:
                    start_position = rjson
                    previous_split = longestSubstringFinder(previous_split, i["objectName"])

                for each_split in splitted_root:
                    start_position = path_finder(start_position, each_split)
                    if (start_position["name"]) == self.bucket_name: previous_split = ""
                if file_extension.search(i["objectName"]):
                    start_position["children"].append(leaf_assignemnt(i))
                else:
                    start_position["children"].append(branch_assignment(i["objectName"],
                                                                        i["objectName"].replace(previous_split, "",
                                                                                                1).replace(
                                                                            "/", "").strip()))
                    previous_split = i["objectName"]
        pp.pprint(rjson)
        return rjson

    def filter_objects(self, data):
        new_value = {}
        new_value["bucketName"] = data["Name"]
        new_value["bucketData"] = []

        for i in data["Contents"]:
            temp = {}
            temp["objectName"] = i["Key"]
            temp["lastModified"] = str(i["LastModified"])
            temp["size"] = i["Size"]
            temp["owner"] = i["Owner"]["DisplayName"]
            new_value["bucketData"].append(temp)
        return new_value

    def list_objects(self, bucket_name, username):
        pp.pprint(self.client.list_objects(Bucket=bucket_name))
        if "Contents" not in self.client.list_objects(Bucket=bucket_name):
            rjson = {}
            rjson["name"] = bucket_name
            rjson["children"] = []
            return rjson
        else:
            return self.data_structure_transformer(self.filter_objects(self.client.list_objects(Bucket=bucket_name)),
                                                   username)

    def get_object(self, bucket, key):
        response = self.client.get_object(Bucket=bucket, Key=key)
        import base64
        base64_encoded_value = base64.standard_b64encode(response["Body"].read())

        def worker():
            status = self.redis_connection.insert_object(key, base64_encoded_value)
            print(status)

        if base64_encoded_value:
            # Used thread to implement Async performance rather than synchronous  way.
            try:
                thread = threading.Thread(target=worker)
                thread.daemon = True
                thread.start()
            except:
                print("Error: unable to insert into Cache")
            return base64_encoded_value
        else:
            return "Failure"

    def upload_object(self, file):
        import base64
        body = base64.b64decode(file["file"])
        if (file["path"] == self.bucket_name):
            file_name = file["name"]
        else:
            file_name = file["path"] + file["name"]
        result = self.client.put_object(Bucket=self.bucket_name, ACL='public-read', Body=body, Key=file_name)

        def worker():
            status = self.redis_connection.insert_object(file_name, file["file"])
            print(status)

        if result["VersionId"]:
            try:
                thread = threading.Thread(target=worker)
                thread.daemon = True
                thread.start()
            except:
                print("Error: unable to update the Cache")
        return result["VersionId"]

    def delete_objects(self, objects):
        result = self.client.delete_objects(Bucket=self.bucket_name, Delete=objects)
        return result["Deleted"][0]["DeleteMarker"]

    def one_folder_up(self, path):
        splitted_path = list(filter(None, path.split("/")))
        del splitted_path[-1]
        return ("/".join(splitted_path) + "/")

    def roll_back(self, files):
        import re
        print("worker started")
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        objects = self.redis_connection.get_keys(pattern="backup:" + files[0]["Key"] + "*")
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

    def create_replace_record(self, find_result, accept_result):
        replace_result = find_result
        print(find_result["accessing_users"])
        print(accept_result)
        temp = find_result["accessing_users"]
        for v in range(len(temp)):
            print(temp[v])
            if temp[v]["name"] == accept_result["username"]:
                print("inside 2")
                print(accept_result["access"])
                print(replace_result["accessing_users"][v])
                replace_result["accessing_users"][v][accept_result["access"]] = True
                print("replace_result", replace_result)
                return replace_result

        file_to_new_append = {"name": accept_result["username"], accept_result["access"]: True}
        print(file_to_new_append)
        find_result["accessing_users"].append(file_to_new_append)
        print(find_result)
        return find_result

    def status_change(self, collection, filter, status):
        if "status" in filter: del filter["status"]
        find_result = self.mongo_connection.find_one(filter, collection)
        find_result["status"] = status
        return self.mongo_connection.replace(filter, find_result, collection)

    def file_accesses_others(self, data):
        results = []
        for j in data:
            temp = {}
            temp["file"] = j["file"]
            for i in j["accessing_users"]:
                temp["name"] = i["name"]
                temp["access"] = ""
                if "read" in i: temp["access"] = temp["access"] + "read "
                if "write" in i: temp["access"] = temp["access"] + "write "
                if "delete" in i: temp["access"] = temp["access"] + "delete"
            results.append(temp)

        return (results)
