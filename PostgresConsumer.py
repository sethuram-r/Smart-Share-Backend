import configparser
from json import loads

from kafka import KafkaConsumer

from AccessManagementService import logging
from AccessManagementService.PostgresCommunicator import PostgresWriteTaskHandler

config = configparser.ConfigParser()
config.read('AccessManagementConfig.ini')

createAccessRequestKey = config['TASKS']['CREATE_ACCESS_REQUEST']
deleteAccessRequestKey = config['TASKS']['DELETE_ACCESS_REQUEST']
approveOrRejectAccessRequest = config['TASKS']['APPROVE_REJECT_ACCESS_REQUEST']


def fileOwnerApproveOrRejectAccessRequest(accessRequestToBeApprovedOrRejected):
    logging.info("Consumer: Inside fileOwnerApproveOrRejectAccessRequest")

    if accessRequestToBeApprovedOrRejected["status"] == "approve":
        del accessRequestToBeApprovedOrRejected["status"]
        PostgresWriteTaskHandler.PostgresWriteTaskHandler().approveAccessRequest(
            accessRequestToBeApprovedOrRejected)
    else:
        del accessRequestToBeApprovedOrRejected["status"]
        PostgresWriteTaskHandler.PostgresWriteTaskHandler().rejectAccessRequest(
            accessRequestToBeApprovedOrRejected)


def createAccessRequest(accessRequest):
    logging.info("Consumer: Inside createAccessRequest")

    PostgresWriteTaskHandler.PostgresWriteTaskHandler().createAccessRequest(accessRequest)


def deleteAccessRequestRecord(accessRequest):
    logging.info("Consumer: Inside deleteAccessRequestRecord")

    PostgresWriteTaskHandler.PostgresWriteTaskHandler().deleteAccessRequestRecord(accessRequest)


def consumer():
    consumer = KafkaConsumer(
        'access_management',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='access-management-group',
        key_deserializer=lambda x: (x.decode('utf-8')),
        value_deserializer=lambda x: loads(x.decode('utf-8')))
    for requests_or_records in consumer:

        if requests_or_records.key == createAccessRequestKey: createAccessRequest(requests_or_records.value)
        if requests_or_records.key == deleteAccessRequestKey: deleteAccessRequestRecord(requests_or_records.value)
        if requests_or_records.key == approveOrRejectAccessRequest: fileOwnerApproveOrRejectAccessRequest(
            requests_or_records.value)


consumer()
