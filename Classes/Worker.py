import requests
from flask import Flask

from Classes import ServiceClassImp

app = Flask(__name__)


class Worker:

    def __init__(self, worker_id, worker_name):
        # GIT repository settings
        self.worker_id = worker_id
        self.worker_name = worker_name
        self.master_address = "http://{0}:{1}/worker".format('127.0.0.1', 8000)

        self.responses = []

    def respond_to_request(self, request_dict):

        print("1------------->", request_dict)

        with app.app_context():
            service = ServiceClassImp.ServiceClassImp(request_dict["param"], request_dict["task"])
            print("service", (service.result))

            response = request_dict
            response["response"] = service.result
            print(response)

            # post result to the server
            response = requests.post(self.master_address, json=response)
            print("response from master------>", response.text)

    def listen_requests(self):
        """ send requests to master for tasks """

        while True:
            # ask the server for a task
            response = requests.get(self.master_address)
            if response.json() == 'Done':
                pass
            else:
                print(response.content)
                data = response.json()
                print(data)
                self.respond_to_request(data)


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--host', type=str, default='127.0.0.1', help='host ip of master.')
    # parser.add_argument('--port', type=int, default=5000, help='port of master.')
    # parser.add_argument('--workerID', type=int, default=3, help='ID to identify worker')
    #
    # FLAGS, unparsed = parser.parse_known_args()

    worker_name = 'worker_{0}'.format(1)
    worker = Worker(1, worker_name)
    worker.listen_requests()


main()
