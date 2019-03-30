from json import dumps

from kafka import KafkaProducer


class ServiceImplementation:

    def __init__(self, request):
        self.request = request

    def signUp(self):

        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], key_serializer=lambda x: x.encode('utf-8'),
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        data_to_placed_in_the_stream = self.request["data"]
        result = producer.send('authentication', key=self.request["task"], value=data_to_placed_in_the_stream)
        if (result.is_done):
            return ({"status": True})
        else:
            return ({"status": False})

    #
    #
    # def register(self):
    #     login_credentials = self.request["data"]
    #     filter = {"username": login_credentials["username"]}
    #     result = self.mongo_connection.update(filter, login_credentials)
    #     if (result.raw_result["updatedExisting"]):
    #         print("The User data is updated successfully.......")
    #         return ({"status": True})
    #     else:
    #         print("The data updation resulted in failure.......")
    #         return ({"status": False})
    #
    # def signUp(self):
    #     result = self.mongo_connection.insert(self.request["data"])
    #     del self.request["data"]["_id"]
    #     if result.acknowledged == True:
    #         print("The User data is inserted successfully.......")
    #         return {"status": True}
    #     else:
    #         print("The data insertion resulted in failure.......")
    #         return ({"status": False})
    #
    # def signIn(self):
    #
    #     login_credentials = self.request["data"]
    #     result = self.mongo_connection.find_one(login_credentials)
    #     if (result) != "":
    #         print("The User data is exists .......")
    #         return ({"status": True})
    #     else:
    #         print("The data doesn't exists.......")
    #         return ({"status": False})
    #
    # def validateSession(self):
    #     username = self.request.get('username')
    #     session_id = self.request.get('sessionid')
    #     result = self.mongo_connection.find_one({"username": username, "authentication_server_sessionId": session_id})
    #     if (result) != "":
    #         print("The User data exists .......")
    #         return {"status": True}
    #     else:
    #         print("The data doesn't exists.......")
    #         return {"status": False}
