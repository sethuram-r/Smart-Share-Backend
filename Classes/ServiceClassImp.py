from Classes import ServiceClass


class ServiceClassImp(ServiceClass.ServiceClass):
    def __init__(self, request, task):
        ServiceClass.ServiceClass.__init__(self, request)
        self.result = self.initiate()

    def initiate(self):
        result = self.send_objects()
        return (result)
