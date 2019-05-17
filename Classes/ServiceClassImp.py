from Classes import ServiceClass


class ServiceClassImp(ServiceClass.ServiceClass):
    def __init__(self, request, mongo_pool, redis_pool):
        print("The ServiceClassImp constructor invoked...........")
        self.mongo_pool = mongo_pool
        self.redis_pool = redis_pool
        ServiceClass.ServiceClass.__init__(self, request)
        self.result = self.initiate()


    def initiate(self):
        result = self.__getattribute__(self.request["task"])()
        return (result)

    def __del__(self):
        print("The ServiceClassImp destructor invoked...........")

        self.mongo_pool.release(self.mongo_connection)
        self.redis_pool.release(self.redis_connection)

