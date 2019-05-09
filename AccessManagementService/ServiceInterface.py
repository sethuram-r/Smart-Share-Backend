from AccessManagementService import ServiceImplementation, ApiImplementation

""" This class is an interface that maps the request to corresponding task handlers."""


class ServiceInterface(ServiceImplementation.ServiceImplementation, ApiImplementation.ApiImplmentation):
    def __init__(self, request):
        super().__init__(request)
        self.result = self.initiate()

    def initiate(self):
        result = self.__getattribute__(self.request["task"])()
        return (result)
