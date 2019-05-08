from CoreService import AmazonS3Access
from CoreService.Redis import RedisAccess

""" This class is used to get data from different data sources """


class DataSourceFactory:

    def getS3Access(self):
        return AmazonS3Access.AmazonS3Access()

    def getRedisAccess(self, role):
        return RedisAccess.RedisAccess().getRedisAccess(role)
