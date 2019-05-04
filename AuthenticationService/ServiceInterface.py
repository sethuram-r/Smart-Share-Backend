from AuthenticationService import ServiceImplementation

""" This class is an interface that maps the request to corresponding task handlers."""

class ServiceInterface(ServiceImplementation.ServiceImplementation):
    def __init__(self, request):
        ServiceImplementation.ServiceImplementation.__init__(self, request)
        self.result = self.initiate()

    def initiate(self):
        result = self.__getattribute__(self.request["task"])()
        return (result)
