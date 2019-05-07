import configparser
from json import loads

from kafka import KafkaConsumer

from AccessManagementService.PostgresCommunicator import PostgresWriteTaskHandler

config = configparser.ConfigParser()
config.read('AccessManagementConfig.ini')

createAccessRequestKey = config['TASKS']['CREATE_ACCESS_REQUEST']
deleteAccessRequestKey = config['TASKS']['DELETE_ACCESS_REQUEST']
approveOrRejectAccessRequest = config['TASKS']['APPROVE_REJECT_ACCESS_REQUEST']


# def FileOwnerApproveOrRejectAccessRequest(accessRequestToBeApprovedOrRejected):
#     if accessRequestToBeApprovedOrRejected["status"] == "approve":
#         PostgresWriteTaskHandler.PostgresWriteTaskHandler(database.Model, database).approveAccessRequest(
#             accessRequestToBeApprovedOrRejected)
#     else:
#         PostgresWriteTaskHandler.PostgresWriteTaskHandler(database.Model, database).rejectAccessRequest(
#             accessRequestToBeApprovedOrRejected)
#

def keyDeserializer(key):
    return key.decode('utf-8')


def valueDeserializer(value):
    return loads(value.decode('utf-8'))

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
        print("requests_or_records----------->", requests_or_records.value)

        """ Based on the key the events are filtered and processed.
         This would have been done by forming a new stream through stream processing using faust"""

        if keyDeserializer(requests_or_records.key) == createAccessRequestKey:
            PostgresWriteTaskHandler.PostgresWriteTaskHandler().createAccessRequest(
                valueDeserializer(requests_or_records.value))

        # if keyDeserializer(requests_or_records.key) == deleteAccessRequestKey:
        #     PostgresWriteTaskHandler.PostgresWriteTaskHandler(database.Model, database).deleteAccessRequestRecord(
        #         valueDeserializer(requests_or_records.value))
        #
        # if keyDeserializer(requests_or_records.key) == approveOrRejectAccessRequest:
        #     FileOwnerApproveOrRejectAccessRequest(valueDeserializer(requests_or_records.value))


consumer()
