import configparser
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("Postgres Management Service")

config = configparser.ConfigParser()
config.read('AccessManagementConfig.ini')
app.config['SQLALCHEMY_DATABASE_URI'] = config['POSTGRES']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
databaseInstance = SQLAlchemy(app)
databaseInstance.metadata.schema = config['POSTGRES']['SCHEMA']

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
