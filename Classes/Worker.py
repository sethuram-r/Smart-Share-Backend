import requests
from flask import Flask

from Classes import ServiceClassImp, MongoConnectionClassPool, RedisConnectionClassPool

app = Flask(__name__)


class Worker:

    def __init__(self, count, mongo_pool, redis_pool):
        self.count = int(count)
        self.master_address = "http://{0}:{1}/worker".format('127.0.0.1', 8000)
        self.responses = []
        self.mongo_pool = mongo_pool
        self.redis_pool = redis_pool


    def respond_to_request(self, request_dict):

        with app.app_context():
            service = ServiceClassImp.ServiceClassImp(request_dict, self.mongo_pool, self.redis_pool)
            request_dict["response"] = service.result

            # post result to the server
            response = requests.post(self.master_address, json=request_dict)

    def listen_requests(self):
        """ send requests to master for tasks """
        while self.count != 0:
            response = requests.get(self.master_address)
            if response.json() == 'Done':
                break
            else:
                data = response.json()
                self.respond_to_request(data)
            self.count = self.count - 1


mongo_pool = MongoConnectionClassPool.MongoConnectionClassPool()
redis_pool = RedisConnectionClassPool.RedisConnectionClassPool()


@app.route('/poll/<count>', methods=['GET'])
def handle_polling(count):
    worker = Worker(count, mongo_pool, redis_pool)
    worker.listen_requests()
    return "", 200
