import base64
import boto3
import configparser

"""This class is used to access the Amazon S3 Cloud. """


class AmazonS3Access:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        aws_access_key_id = config['DEFAULT']['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = config['DEFAULT']['AWS_SECRET_ACCESS_KEY']
        region_name = config['DEFAULT']['AWS_REGION_NAME']
        self.__client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=region_name)

    def listObjects(self, bucketName):
        return self.__client.list_objects(Bucket=bucketName)

    def getObject(self, bucket, key):
        return self.__client.get_object(Bucket=bucket, Key=key)

    def deleteObjects(self, objects, bucketName):
        result = self.__client.delete_objects(Bucket=bucketName, Delete=objects)
        return result["Deleted"][0]["DeleteMarker"]

    def listObjectsForFolder(self, bucketName, selectedFolder):
        return self.__client.list_objects_v2(Bucket=bucketName, prefix=selectedFolder)

    def uploadObject(self, file, bucketName):
        body = base64.b64decode(file["file"])
        if (file["path"] == bucketName):
            fileName = file["name"]
        else:
            fileName = file["path"] + file["name"]
        uploadResult = self.client.put_object(Bucket=self.bucketName, ACL='public-read', Body=body, Key=fileName)
        if uploadResult["VersionId"]:
            return True
        else:
            return False

    def uploadSavepoint(self, bucketName, fileName, fileContent):
        body = base64.b64decode(fileContent)
        uploadResult = self.client.put_object(Bucket=self.bucketName, ACL='public-read', Body=body, Key=fileName)
        if uploadResult["VersionId"]:
            return True
        else:
            return False
