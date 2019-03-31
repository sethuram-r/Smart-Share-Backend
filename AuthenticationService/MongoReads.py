from AuthenticationService import MongoAccess

""" This class is used to access mongo DB by just focusing on business details
 and abstracting the technical implementation details of mongo DB"""


class MongoReads:

    def __init__(self):
        self.mongoConnection = MongoAccess.MongoAccess()

    def findOneRecord(self, record, collection):
        collectionToBeChecked = self.mongoConnection.return_collection(collection)
        existingRecord = self.mongoConnection.find_one(record, collectionToBeChecked)
        return existingRecord
