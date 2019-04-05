import pprint as pp
import re

""" This class transforms the results from the data source to a hierarchical structure. """


class FileStructureTransformer:

    def __init__(self, username, bucketName, accesssDetailsForFilesAndFolders):
        self.userName = username
        self.bucketName = bucketName
        self.accessDetailsForFilesAndFolders = accesssDetailsForFilesAndFolders

    def accessAssignmentToEachFileAndFolder(self, node, metadata):  # untested
        node["owner"] = metadata["owner"]
        for user in metadata["accessing_users"]:
            if (user["name"] == self.userName):
                if "read" in user: node["read"] = user["read"]
                if "write" in user: node["write"] = user["write"]
                if "delete" in user: node["delete"] = user["delete"]
        return node

    def findAccessDetailsForSpecificFileorFolder(self, neededFileOrFolder):

        for eachFileorFolder in self.accessDetailsForFilesAndFolders:  # untested
            if eachFileorFolder["file"] == neededFileOrFolder:
                return eachFileorFolder

    def leaf_assignemnt(self, object):
        temp = object["objectName"].split("/")
        del temp[-1]
        root_folder_name = "/".join(temp) + "/"
        temp = {}
        temp["name"] = object["objectName"].replace(root_folder_name, "").strip()
        temp["trueName"] = object["objectName"]
        temp["value"] = round(object["size"] / 1024, 2)
        metadata = self.findAccessDetailsForSpecificFileorFolder(object["objectName"])
        if (metadata): temp = self.accessAssignmentToEachFileAndFolder(temp, metadata)
        return temp

    def branch_assignment(self, original_name, name):
        temp = {}
        temp["name"] = name
        temp["trueName"] = original_name
        temp["children"] = []

        ## replaced the database call with API Data

        metadata = self.findAccessDetailsForSpecificFileorFolder(temp["trueName"])
        if (metadata): temp = self.accessAssignmentToEachFileAndFolder(temp, metadata)
        return temp

    def path_finder(self, start_position, folder):
        if start_position["children"] == []:
            return start_position
        else:
            for a in start_position["children"]:
                if a["name"] == folder:
                    return a
            return start_position

    def longestSubstringFinder(self, string1, string2):
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

    def dataStructureTransformerPipeline(self, filteredResult):

        """ transforms the filtered s3 result"""

        transformedResult = {}
        transformedResult["name"] = filteredResult["bucketName"]
        transformedResult["children"] = []
        file_extension_regex = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\....)$")

        start_position = transformedResult
        previous_split = ""
        file_extension = re.compile("([a-zA-Z0-9\s_\\.\-\(\):])+(\..*)$")
        for i in filteredResult["bucketData"]:
            if file_extension_regex.search(i["objectName"]) and "/" not in i["objectName"]:
                transformedResult["children"].append(self.leaf_assignemnt(i))
            elif i["objectName"].endswith('/') or file_extension.search(i["objectName"]):
                if file_extension.search(i["objectName"]):
                    splitted_root = list(filter(None, i["objectName"].split("/")))
                    del splitted_root[-1]
                else:
                    splitted_root = list(filter(None, i["objectName"].split("/")))
                if previous_split not in splitted_root:
                    start_position = transformedResult
                    previous_split = self.longestSubstringFinder(previous_split, i["objectName"])

                for each_split in splitted_root:
                    start_position = self.path_finder(start_position, each_split)
                    if (start_position["name"]) == self.bucketName: previous_split = ""
                if file_extension.search(i["objectName"]):
                    start_position["children"].append(self.leaf_assignemnt(i))
                else:
                    start_position["children"].append(self.branch_assignment(i["objectName"],
                                                                             i["objectName"].replace(previous_split, "",
                                                                                                     1).replace(
                                                                                 "/", "").strip()))
                    previous_split = i["objectName"]
        pp.pprint(transformedResult)
        return transformedResult

    def filterValidS3Result(self, validS3Result):

        print("validS3Result------------>", validS3Result)  # no idea why and what is getting filtered

        filteredResult = {}
        filteredResult["bucketName"] = validS3Result["Name"]
        filteredResult["bucketData"] = []

        for eachContent in validS3Result["Contents"]:
            requiredContentInformation = {}
            requiredContentInformation["objectName"] = eachContent["Key"]
            requiredContentInformation["lastModified"] = str(eachContent["LastModified"])
            requiredContentInformation["size"] = eachContent["Size"]
            requiredContentInformation["owner"] = eachContent["Owner"]["DisplayName"]
            filteredResult["bucketData"].append(requiredContentInformation)
        return filteredResult

    def transformInvalidInput(self, bucketName):
        s3TransformedResult = {}
        s3TransformedResult["name"] = bucketName
        s3TransformedResult["children"] = []
        return s3TransformedResult

    def checkInput(self, s3ResultToBeTransformed):

        """ Function checks the validity of the s3 Result. """

        if "Contents" not in s3ResultToBeTransformed:
            return False
        else:
            return True

    def transformationProcessPipeline(self, s3ResultToBeTransformed):
        validInput = self.checkInput(s3ResultToBeTransformed)
        if validInput == False:
            return self.transformInvalidInput(self.bucketName)
        else:

            # transformation begins

            filteredResult = self.filterValidS3Result(s3ResultToBeTransformed)
            transformedResult = self.dataStructureTransformerPipeline(filteredResult)
            return transformedResult
