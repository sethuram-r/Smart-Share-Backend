from CoreService import AmazonS3Access

""" This class is used to get data from different data sources """


class DataSourceFactory:

    def getS3Access(self):
        """ This function gives the access to s3 """

        return AmazonS3Access.AmazonS3Access()
