import configparser
from json import dumps
from time import sleep

from kafka import KafkaProducer

from AccessManagementService import logging
from AccessManagementService.PostgresCommunicator import PostgresReadTaskHandler

""" This class is the Access Management implementation  done through various task handlers."""


class ServiceImplementation:

    def __init__(self, request):
        super().__init__(request)
        config = configparser.ConfigParser()
        config.read('AccessManagementConfig.ini')
        self.request = request
        # self.modelInstance = modelInstance
        # self.databaseInstance = databaseInstance
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                      value_serializer=lambda x:
                                      dumps(x).encode('utf-8'))

    def createAccessRequest(self):

        logging.info("Inside createAccessRequest")

        data_to_placed_in_the_stream = self.request["param"]
        result = self.producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        sleep(5)
        if (result.is_done):
            logging.debug("Access Request is initiated")
            return ({"status": True})
        else:
            logging.warning("Access Request is not initiated")
            return ({"status": False})

    def deleteApprovedOrRejectedAccessRequest(self):

        logging.info("Inside deleteApprovedOrRejectedAccessRequest")

        data_to_placed_in_the_stream = self.request["data"]
        result = self.producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        sleep(5)
        if (result.is_done):
            logging.debug("Delete Request is initiated")
            return ({"status": True})
        else:
            logging.warning("Delete Request is not initiated")
            return ({"status": False})

    def FileOwnerApproveOrRejectAccessRequest(self):

        logging.info("Inside FileOwnerApproveOrRejectAccessRequest")

        data_to_placed_in_the_stream = self.request["data"]
        result = self.producer.send('access_management', key=self.request["task"], value=data_to_placed_in_the_stream)
        sleep(5)
        if (result.is_done):
            logging.debug("Approve or Reject Request is initiated")
            return ({"status": True})
        else:
            logging.warning("Approve or Reject Request is not initiated")
            return ({"status": False})


    def getListOfUsersAccessingOwnersFiles(self):

        logging.info("Inside getListOfUsersAccessingOwnersFiles")

        ownerName = self.request["param"].get('username')
        return PostgresReadTaskHandler.PostgresReadTaskHandler().getFilesInformationForSpecificUser(
            ownerName)

    def getAccessRequestsCreatedByUser(self):

        logging.info("Inside getAccessRequestsCreatedByUser")

        username = self.request["param"].get('username')
        return PostgresReadTaskHandler.PostgresReadTaskHandler().getAccessRequestsCreatedByTheUser(
            username)

    def getAccessRequestsToBeApprovedByOwnerOfTheFile(self):

        logging.info("Inside getAccessRequestsToBeApprovedByOwnerOfTheFile")

        ownerName = self.request["param"].get('owner')
        return PostgresReadTaskHandler.PostgresReadTaskHandler().getAccessRequestsForOwnerToApproval(
            ownerName)
