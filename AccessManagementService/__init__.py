import configparser

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("Postgres Management Service")

config = configparser.ConfigParser()
config.read('AccessManagementConfig.ini')
app.config['SQLALCHEMY_DATABASE_URI'] = config['POSTGRES']['SQLALCHEMY_DATABASE_URI']
databaseInstance = SQLAlchemy(app)
databaseInstance.metadata.schema = config['POSTGRES']['SCHEMA']
