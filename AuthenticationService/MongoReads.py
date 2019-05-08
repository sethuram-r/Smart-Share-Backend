from AuthenticationService import MongoAccess, logging

""" This class is used to access mongo DB by just focusing on business details
 and abstracting the technical implementation details of mongo DB"""


class MongoReads:

    def __init__(self):
        self.mongoConnection = MongoAccess.MongoAccess()

    def findOneRecord(self, record, collection):
        logging.info("Inside findOneRecord")

        collectionToBeChecked = self.mongoConnection.return_collection(collection)
        existingRecord = self.mongoConnection.find_one(record, collectionToBeChecked)
        logging.debug("Existing Record %s", existingRecord)
        return existingRecord
