import configparser
from json import dumps

from kafka import KafkaProducer

from AccessManagementService.PostgresCommunicator import PostgresReadTaskHandler

""" This class is the Access Management implementation  done through various task handlers."""


class ServiceImplementation:

    def __init__(self, request, modelInstance, databaseInstance):
        super().__init__(request, modelInstance, databaseInstance)
        config = configparser.ConfigParser()
        config.read('AccessManagementConfig.ini')
        self.request = request
        self.modelInstance = modelInstance
        self.databaseInstance = databaseInstance
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                      value_serializer=lambda x:
                                      dumps(x).encode('utf-8'))

    def createAccessRequest(self):  # accessRequest has been renamed to this function name

        data_to_placed_in_the_stream = self.request["param"]
        result = self.producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})

    def deleteApprovedOrRejectedAccessRequest(self):  # deleteRecord has been renamed to this function --kafka

        data_to_placed_in_the_stream = self.request["data"]
        result = self.producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})

    def FileOwnerApproveOrRejectAccessRequest(self):  # requestStatus has been renamed to this function --kafka

        data_to_placed_in_the_stream = self.request["data"]
        result = self.producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})


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
