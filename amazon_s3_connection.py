import boto3
import pprint as pp
import io
import datetime
from dateutil.tz import tzutc




def data_structure_transformer(value):
    import pprint as pp
    import re

    rjson = {}
    rjson["name"] = value["bucketName"]
    rjson["children"] = []

    def leaf_assignemnt(object, root_folder_name):
        temp = {}
        temp["name"] = object["objectName"].replace(root_folder_name, "").strip()
        temp["trueName"] = object["objectName"]
        temp["value"] = round(object["size"]/1024,2)
        return temp

    def branch_assignment(original_name,name):
        temp = {}
        temp["name"] = name
        temp["trueName"] = original_name
        temp["children"] = None
        return temp

    def path_finder(start_position, folder):
        for a in start_position["children"]:
            if a["name"] == folder:
                if a["children"] == None:
                    a["children"] = []
                return a

    folder_name = ""
    for i in value["bucketData"]:
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\....)$")
        if folder_name == "" or folder_name not in i["objectName"]:
            if "/" in i["objectName"] and i["objectName"].count("/") == 1:
                folder_name = i["objectName"]
                rjson["children"].append(branch_assignment(i["objectName"],i["objectName"].replace("/", "").strip()))
            elif file_extension.search(i["objectName"]) and "/" not in i["objectName"]:
                rjson["children"].append(leaf_assignemnt(i, folder_name))
        else:
            splitted_root = folder_name.split("/")
            start_position = rjson
            for each_split in splitted_root:
                if each_split != "":
                    start_position = path_finder(start_position, each_split)
            if file_extension.search(i["objectName"]) and folder_name in i["objectName"]:
                start_position["children"].append(leaf_assignemnt(i, folder_name))
            elif folder_name in i["objectName"]:
                start_position["children"].append(
                    branch_assignment(i["objectName"],i["objectName"].replace(folder_name, "").replace("/", "")))
                folder_name = i["objectName"]
            else:
                rjson["children"].append(leaf_assignemnt(i, folder_name))

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
    pp.pprint(client.list_objects(Bucket = bucket_name))
    return data_structure_transformer(filter_objects(client.list_objects(Bucket = bucket_name)))

def get_object(bucket,key):
    response = client.get_object(Bucket=bucket,Key=key)
    print(response)
    return response["Body"].read()

def upload_object(file):
    import base64
    print(file["name"])
    print(file["path"])
    body = base64.b64decode(file["file"])
    if(file["path"] =="file.server.1"):
        file_name = file["name"]
    else:
        file_name = file["path"] + file["name"]

    result =  client.put_object(Bucket='file.server.1', ACL='public-read', Body=body, Key=file_name)
    return result["VersionId"]