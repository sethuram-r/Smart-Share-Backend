import configparser
import json

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from AccessManagementService import ServiceInterface, logging

app = Flask("Access Management Service")

config = configparser.ConfigParser()
config.read('AccessManagementConfig.ini')
app.config['SQLALCHEMY_DATABASE_URI'] = config['POSTGRES']['SQLALCHEMY_DATABASE_URI']
databaseInstance = SQLAlchemy(app)
databaseInstance.metadata.schema = config['POSTGRES']['SCHEMA']


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
    logging.info("Transformed Request From Web %s", transformed_request)
    service = ServiceInterface.ServiceInterface(transformed_request, databaseInstance.Model, databaseInstance)
    logging.info("Response  %s", service.result)
    return jsonify(service.result)
