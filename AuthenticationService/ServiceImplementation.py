import configparser
import hashlib
import random
import string
from json import dumps

from kafka import KafkaProducer

from AuthenticationService import DataBaseInterface

""" This class is the core implementation of Business logic done through various task handlers."""

class ServiceImplementation:

    def __init__(self, request):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.username = config['HELPERS']['USER_NAME']
        self.sessionId = config['HELPERS']['SESSION_ID']
        self.request = request

    """ ----------------------------------------Helper Functions------------------------------------------------"""

    def encryptStringToSHA(self, stringToBeHashed):
        shaSignature = hashlib.sha256(stringToBeHashed.encode()).hexdigest()
        return shaSignature

    def generateRandomKey(self):

        """ Function to generate random key and it is hashed using sha-256  """
        randomKey = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return self.encryptStringToSHA(randomKey)

    """ ----------------------------------------Domain Functions------------------------------------------------"""


    def signUp(self):

        """ Function to submit the signup request to the kafka stream """

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        data_to_placed_in_the_stream = self.request["data"]
        result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})

    def signIn(self):

        """ Function to verify the incoming signin request and return the session key
            along with pushing the session key to kafka stream """

        loginCredentialsToBeVerified = self.request["data"]

        print("loginCredentialsToBeVerified-------->", loginCredentialsToBeVerified)

        login_credentials_verification_status = DataBaseInterface.DataBaseInterface.findSignInRecordInDatabase(
            loginCredentialsToBeVerified)
        if (login_credentials_verification_status) != "":
            randomKey = self.generateRandomKey()

            # record preparation for producing kafka event begins

            duplicatedLoginCredentials = self.request["data"]
            del duplicatedLoginCredentials[self.username]
            duplicatedLoginCredentials[self.sessionId] = randomKey

            # put the record in the kafka stream so that it can be consumed by other consumers

            producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                     value_serializer=lambda x:
                                     dumps(x).encode('utf-8'))

            data_to_placed_in_the_stream = duplicatedLoginCredentials
            result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
            if (result.is_done):
                return ({"status": True, self.sessionId: randomKey})
            else:
                return ({"status": False})
        else:
            print("The data doesn't exists.......")
            return ({"status": False})

    def validateSession(self):

        """ Function to validate user sessions"""

        usersSessionDetailsToVerify = self.request["param"]

        print("usersSessionDetailsToVerify-------->", usersSessionDetailsToVerify)

        usersSessionDetailsVerificationStatus = DataBaseInterface.DataBaseInterface.findSessionRecordInDatabase(
            usersSessionDetailsToVerify)
        if (usersSessionDetailsVerificationStatus) != "":

            print("This is a valid session info .......")
            return {"status": True}
        else:
            print("This is not a valid session info.......")
            return {"status": False}

    def logOut(self):

        userToBeLoggedOut = self.request["param"]

        print("userToBeLoggedOut-------->", userToBeLoggedOut)

        # put the record in the kafka stream so that it can be consumed by other consumers

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        data_to_placed_in_the_stream = userToBeLoggedOut
        result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            print("The User has been logged out .......")
            return ({"status": True})
        else:
            print("The User has not been logged out.......")
            return ({"status": False})
