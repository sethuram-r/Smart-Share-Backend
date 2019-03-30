import json

from flask import Flask, request, jsonify

from AuthenticationService import ServiceInterface

app = Flask("Authentication Service")


def request_preparation(request, path):
    temp = {}
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
    return temp


@app.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    transformed_request = request_preparation(request, path)
    print("transformed_request-------------->", transformed_request)
    service = ServiceInterface.ServiceInterface(transformed_request)
    print("result---------------->", service.result)
    return jsonify(service.result)
