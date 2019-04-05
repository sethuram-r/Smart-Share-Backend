from CoreService import AmazonS3Access
from CoreService.Redis import RedisAccess

""" This class is used to get data from different data sources """


class DataSourceFactory:

    def getS3Access(self):
        """ This function gives the access to s3 """

        return AmazonS3Access.AmazonS3Access()

    def getRedisAccess(self, role):
        """ This function gives the access to redis """

        return RedisAccess.RedisAccess(role)
