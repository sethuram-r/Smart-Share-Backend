import configparser

import boto3

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
