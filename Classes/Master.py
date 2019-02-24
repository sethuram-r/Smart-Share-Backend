import json

import polling
import requests as url_request
from flask import Flask, request, jsonify

from Classes import ServiceClassImp, MongoConnectionClassPool, RedisConnectionClassPool

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024

requests = []
responses = {}

mongo_pool = MongoConnectionClassPool.MongoConnectionClassPool()
redis_pool = RedisConnectionClassPool.RedisConnectionClassPool()

@app.route('/worker', methods=['GET'])
def get():
    """ worker gets task to be done from here"""

    if len(requests) == 0:
        request_to_process = 'Done'

    else:
        request_to_process = requests.pop(0)
        print("request_to_process------->", request_to_process)

    response = jsonify(request_to_process)
    response.status_code = 200
    return response


@app.route('/worker', methods=['POST'])
def post():

    """ worker puts back the result here"""

    if request:
        data = request.json
        print("data", data)
        responses[data["id"]] = data
        return "success"
    else:
        raise NotImplementedError


@app.route('/getObject', methods=['GET'])
def get_object(object=""):
    parameters = {}
    temp = {}
    for i in request.args.keys():
        parameters[i] = request.args.get(i)
    temp["param"] = parameters
    temp["task"] = request.path.replace("/", "").strip()
    service = ServiceClassImp.ServiceClassImp(temp, mongo_pool, redis_pool)
    return service.result


@app.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    result = request_preparation(request, path)
    print("result---------------->", result)
    return jsonify(result)


def request_preparation(request, path):
    current_size_of_requests = len(requests)
    temp = {}
    id = current_size_of_requests + 1
    temp["id"] = id
    if request.method == 'GET':

        """ Extracting all the query parameters from the request"""
        parameters = {}
        for i in request.args.keys():
            parameters[i] = request.args.get(i)

        print("args", parameters)
        temp["param"] = parameters
        temp["task"] = path
    else:
        data = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
        temp["data"] = data
        temp["task"] = path
    print(temp)
    requests.append(temp)

    print("Number of requests-------", len(requests))

    """ Initiating (Polling) the worker immediately after giving request doesn't pickup the count of requests that are added
     after the polling and hence results in the worker not processing that request"""

    while True:
        if id in responses and responses[id]["task"] == path:
            result = (responses[id]["response"])
            break
        else:
            print("waiting for the results from worker.......")
            """ Polling in this place means that the program looks for result in the reponses if not available then it asks
            the workers to get the jobs from request and this also considers the requests that are added later on and initiates 
            polling"""
            polling.poll(

                lambda: url_request.get('http://127.0.0.1:6000/poll/' + str(len(requests))).status_code == 200,
                step=30,
                poll_forever=True
            )

    del responses[id]
    return result
