import configparser
import hashlib
import random
import string
from json import dumps
from time import sleep

from kafka import KafkaProducer

from AuthenticationService import DataBaseInterface, logging

""" This class is the core implementation of Business logic done through various task handlers."""

class ServiceImplementation:

    def __init__(self, request):
        config = configparser.ConfigParser()
        config.read('AuthenticationConfig.ini')
        self.username = config['HELPERS']['USER_NAME']
        self.sessionId = config['HELPERS']['SESSION_ID']
        self.request = request

    """ ----------------------------------------Helper Functions------------------------------------------------"""

    def encryptStringToSHA(self, stringToBeHashed):
        shaSignature = hashlib.sha256(stringToBeHashed.encode()).hexdigest()
        return shaSignature

    def generateRandomKey(self):

        """ Function to generate random key and it is hashed using sha-256  """

        logging.debug("Inside generateRandomKey")

        randomKey = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return self.encryptStringToSHA(randomKey)

    """ ----------------------------------------Domain Functions------------------------------------------------"""


    def signUp(self):

        """ Function to submit the signup request to the kafka stream """
        logging.info("Inside signUp")

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        data_to_placed_in_the_stream = self.request["data"]

        result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
        sleep(5)
        if (result.is_done):
            logging.debug("Successfully pushed to the stream")
            return ({"status": True})
        else:
            logging.debug("Failed to push to the stream")
            return ({"status": False})

    def signIn(self):

        logging.info("Inside signIn")

        loginCredentialsToBeVerified = self.request["data"]
        login_credentials_verification_status = DataBaseInterface.DataBaseInterface().findSignInRecordInDatabase(
            loginCredentialsToBeVerified)

        if (login_credentials_verification_status) is not None:
            randomKey = self.generateRandomKey()

            # record preparation for producing kafka event begins

            duplicatedLoginCredentials = self.request["data"]
            del duplicatedLoginCredentials["password"]
            duplicatedLoginCredentials[self.sessionId] = randomKey

            # put the record in the kafka stream so that it can be consumed by other consumers

            producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                     value_serializer=lambda x:
                                     dumps(x).encode('utf-8'))

            data_to_placed_in_the_stream = duplicatedLoginCredentials
            result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
            sleep(5)
            if (result.is_done):
                logging.debug("Successfully pushed to the stream")
                return ({"status": True, self.sessionId: randomKey})
            else:
                logging.debug("Failed to push to the stream")
                return ({"status": False})
        else:
            logging.debug("Invalid Login Credentials")
            return ({"status": False})

    def validateSession(self):

        """ Function to validate user sessions"""
        logging.info("Inside validateSession")

        usersSessionDetailsToVerify = self.request["param"]
        usersSessionDetailsVerificationStatus = DataBaseInterface.DataBaseInterface().findSessionRecordInDatabase(
            usersSessionDetailsToVerify)
        if (usersSessionDetailsVerificationStatus) is not None:
            logging.debug("Valid Session Details")
            return {"status": True}
        else:
            logging.debug("Invalid Session Details")
            return {"status": False}

    def logOut(self):

        logging.info("Inside logOut")
        userToBeLoggedOut = self.request["param"]
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        data_to_placed_in_the_stream = userToBeLoggedOut
        result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
        sleep(5)
        if (result.is_done):
            logging.debug("Successfully logged out")
            return ({"status": True})
        else:
            logging.debug("Error in logout")
            return ({"status": False})
