import configparser

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("Postgres Management Service")

config = configparser.ConfigParser()
config.read('AccessManagementConfig.ini')
app.config['SQLALCHEMY_DATABASE_URI'] = config['POSTGRES']['SQLALCHEMY_DATABASE_URI']
databaseInstance = SQLAlchemy(app)
databaseInstance.metadata.schema = config['POSTGRES']['SCHEMA']


class ObjectRelationalModel:
    # def __init__(self):
    #     self.owner = Owner()
    #     self.file = File()
    #     self.fileUserAccess = FileUserAccess()
    #     self.permissionsAssigned = PermissionsAssigned()
    #     self.user = User()
    class Owner(databaseInstance.Model):
        id = databaseInstance.Column(databaseInstance.Integer, primary_key=True)
        name = databaseInstance.Column(databaseInstance.Text)
        files = databaseInstance.relationship('File', lazy=True)

    class File(databaseInstance.Model):
        id = databaseInstance.Column(databaseInstance.Integer, primary_key=True)
        name = databaseInstance.Column(databaseInstance.Text)
        ownerId = databaseInstance.Column(databaseInstance.Integer, databaseInstance.ForeignKey('owner.id'),
                                          name="owner_id")
        owner = databaseInstance.relationship("Owner")  ### added apart from tested sample
        users = databaseInstance.relationship("FileUserAccess", backref="file")

    class FileUserAccess(databaseInstance.Model):
        fileId = databaseInstance.Column(databaseInstance.Integer, databaseInstance.ForeignKey('file.id'),
                                         primary_key=True, name="file_id")
        userId = databaseInstance.Column(databaseInstance.Integer, databaseInstance.ForeignKey('user.id'),
                                         primary_key=True, name="user_id")
        accessId = databaseInstance.Column(databaseInstance.Integer,
                                           databaseInstance.ForeignKey('permissions_assigned.id'), name="access_id")
        accessGiven = databaseInstance.relationship('PermissionsAssigned')

    class User(databaseInstance.Model):
        id = databaseInstance.Column(databaseInstance.Integer, primary_key=True)
        name = databaseInstance.Column(databaseInstance.Text)
        files = databaseInstance.relationship("FileUserAccess", backref="user")

    class PermissionsAssigned(databaseInstance.Model):
        id = databaseInstance.Column(databaseInstance.Integer, primary_key=True)
        read = databaseInstance.Column(databaseInstance.Boolean)
        write = databaseInstance.Column(databaseInstance.Boolean)
        delete = databaseInstance.Column(databaseInstance.Boolean)

        def __repr__(self):
            return '<PermissionsAssigned %r %r %r>' % (
                self.read, self.write, self.delete)
