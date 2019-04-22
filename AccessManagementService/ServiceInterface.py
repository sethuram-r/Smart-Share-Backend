from AccessManagementService import ServiceImplementation

""" This class is an interface that maps the request to corresponding task handlers."""


class ServiceInterface(ServiceImplementation.ServiceImplementation):
    def __init__(self, request, modelInstance, databaseInstance):
        ServiceImplementation.ServiceImplementation.__init__(self, request, modelInstance, databaseInstance)
        self.result = self.initiate()

    def initiate(self):
        result = self.__getattribute__(self.request["task"])()
        return (result)
