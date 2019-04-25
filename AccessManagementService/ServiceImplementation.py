import configparser
from json import dumps

from kafka import KafkaProducer

from AccessManagementService.PostgresCommunicator import PostgresWriteTaskHandler, PostgresReadTaskHandler

""" This class is the Access Management implementation  done through various task handlers."""


class ServiceImplementation:

    def __init__(self, request, modelInstance, databaseInstance):
        super().__init__(self, request, modelInstance, databaseInstance)
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.request = request
        self.modelInstance = modelInstance
        self.databaseInstance = databaseInstance

    def createAccessRequest(self):  # accessRequest has been renamed to this function name

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        data_to_placed_in_the_stream = self.request["param"]
        result = producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})

    def FileOwnerApproveOrRejectAccessRequest(self):  # requestStatus has been renamed to this function

        accessRequestToBeApprovedOrRejected = self.request["data"]
        if accessRequestToBeApprovedOrRejected["status"] == "approve":
            return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                     self.databaseInstance).approveAccessRequest(
                accessRequestToBeApprovedOrRejected)
        else:
            return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                     self.databaseInstance).rejectAccessRequest(
                accessRequestToBeApprovedOrRejected)

    def deleteApprovedOrRejectedAccessRequest(self):  # deleteRecord has been renamed to this function
        requestToBeDeleted = self.request["data"]
        return PostgresWriteTaskHandler.PostgresWriteTaskHandler(self.modelInstance,
                                                                 self.databaseInstance).deleteAccessRequestRecord(
            requestToBeDeleted)

    def getListOfUsersAccessingOwnersFiles(self):
        ownerName = self.request["param"].get('username')
        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).getFilesInformationForSpecificUser(
            ownerName)

    def getAccessRequestsCreatedByUser(self):
        username = self.request["param"].get('username')
        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).getAccessRequestsCreatedByTheUser(
            username)

    def getAccessRequestsToBeApprovedByOwnerOfTheFile(self):
        ownerName = self.request["param"].get('owner')
        return PostgresReadTaskHandler.PostgresReadTaskHandler(self.modelInstance,
                                                               self.databaseInstance).getAccessRequestsForOwnerToApproval(
            ownerName)
