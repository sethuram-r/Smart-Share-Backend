import pprint as pp
import threading

import redis_connection as rc


def data_structure_transformer(value):
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
                if (start_position["name"]) == "file.server.1": previous_split = ""
            if file_extension.search(i["objectName"]):
                start_position["children"].append(leaf_assignemnt(i))
            else:
                start_position["children"].append(branch_assignment(i["objectName"],
                                                                    i["objectName"].replace(previous_split, "").replace(
                                                                        "/", "").strip()))
                previous_split = i["objectName"]
    pp.pprint(rjson)
    return rjson


def filter_objects(data):
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


def list_buclets():
    return client.list_buckets()


def list_objects(bucket_name):
    pp.pprint(client.list_objects(Bucket=bucket_name))
    return data_structure_transformer(filter_objects(client.list_objects(Bucket=bucket_name)))


def get_object(bucket, key):
    response = client.get_object(Bucket=bucket, Key=key)
    import base64
    base64_encoded_value = base64.standard_b64encode(response["Body"].read())

    def worker():
        status = rc.insert_object(key, base64_encoded_value)
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


def upload_object(file):
    import base64
    body = base64.b64decode(file["file"])
    if (file["path"] == "file.server.1"):
        file_name = file["name"]
    else:
        file_name = file["path"] + file["name"]
    result = client.put_object(Bucket='file.server.1', ACL='public-read', Body=body, Key=file_name)

    def worker():
        status = rc.insert_object(file_name, file["file"])
        print(status)

    if result["VersionId"]:
        try:
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
        except:
            print("Error: unable to update the Cache")
    return result["VersionId"]


def delete_objects(objects):
    result = client.delete_objects(Bucket='file.server.1', Delete=objects)
    return result["Deleted"][0]["DeleteMarker"]
