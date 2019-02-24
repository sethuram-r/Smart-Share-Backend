class DatabaseFactoryClass():

    def __init__(self, mongo_pool, redis_pool):
        self.mongo_pool = mongo_pool
        self.redis_pool = redis_pool

    def getDatbase(self, name):
        if name == "mongo":
            return self.mongo_pool.acquire()

        if name == "redis":
            return self.redis_pool.acquire()
