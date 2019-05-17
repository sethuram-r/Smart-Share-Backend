from AccessManagementService.PostgresCommunicator.Models import ObjectRelationalModel
from AccessManagementService import databaseInstance


class ModelFactory:

    def __init__(self):
        self.objectRelationalModel = ObjectRelationalModel.ObjectRelationalModel()
        tables = ["owner", "file", "file_user_access", "user", "permissions_assigned", "access_request"]
        tableExists = [databaseInstance.engine.has_table(table, schema="access_management") for table in tables]
        if False in tableExists: databaseInstance.create_all()

    def getAccessRequestObject(self):
        return self.objectRelationalModel.AccessRequest()

    def getAccessRequestObjectToBeDeletedOrApprovedOrRejected(self, accessRequestToBeDeleted):
        accessRequestObject = self.objectRelationalModel.AccessRequest()
        return accessRequestObject.query.filter_by(**accessRequestToBeDeleted).first()

    def getAccessRequestsOfTheUser(self, userName):
        accessRequestObject = self.getAccessRequestObject()
        return accessRequestObject.query.filter_by(userName=userName).all()

    def getAccessRequestsOfTheOwner(self, ownerName):
        accessRequestObject = self.getAccessRequestObject()
        return accessRequestObject.query.filter_by(ownerOfFile=ownerName).all()

    def getFileAndItsAccessingUsersModel(self):

        modelObjects = (self.objectRelationalModel.Owner(),
                        self.objectRelationalModel.File(), self.objectRelationalModel.FileUserAccess(),
                        self.objectRelationalModel.PermissionsAssigned(), self.objectRelationalModel.User())
        return modelObjects

    def getFileAndItsAccessingUsersObject(self, numberOfAccessingUsers):

        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        file = FileObject
        file.owner = OwnerObject
        for eachAccessingUser in range(numberOfAccessingUsers):
            fileUserAccessAssociationObject = FileUserAccessObject
            fileUserAccessAssociationObject.accessId = PermissionsAssignedObject
            fileUserAccessAssociationObject.user = UserObject
            file.users.append(fileUserAccessAssociationObject)
        return file

    def getFileAndItsAccessingUsersObjectForNonExistingFile(self, numberOfAccessingUsers=1):
        return self.getFileAndItsAccessingUsersObject(numberOfAccessingUsers)

    def accessDetailsFormatter(self, access):
        accessRecord = {}
        accessRecord["read"] = False
        accessRecord["write"] = False
        accessRecord["delete"] = False
        accessRecord[access] = True
        return accessRecord

    def accessDetailsToBeUpdatedForThatUser(self, existingAccess, accessToUpdate):
        existingAccessInDictionaryFormat = existingAccess.__dict__
        if accessToUpdate in existingAccessInDictionaryFormat:
            existingAccessInDictionaryFormat[accessToUpdate] = True
        return existingAccessInDictionaryFormat

    def getFileAndItsAccessingUsersObjectForExistingFile(self, accessRequestToBeApproved):

        fileName = accessRequestToBeApproved["file"]
        ownerName = accessRequestToBeApproved["ownerOfFile"]
        userName = accessRequestToBeApproved["userName"]

        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()

        ownerData = OwnerObject.query.filter_by(name=ownerName).first()
        accessingUsersOfGivenFileData = FileObject.query.filter_by(name=fileName, ownerId=ownerData.id).first()

        for eachFileUserAssoc in accessingUsersOfGivenFileData.users:
            if eachFileUserAssoc.user.name == userName:
                accessDetails = self.accessDetailsToBeUpdatedForThatUser(eachFileUserAssoc.accessGiven,
                                                                         accessRequestToBeApproved["accessType"])
                eachFileUserAssoc.accessId = PermissionsAssignedObject.query.filter_by(read=accessDetails["read"],
                                                                                       write=accessDetails["write"],
                                                                                       delete=accessDetails[
                                                                                           "delete"]).first().id
                return accessingUsersOfGivenFileData

        accessDetails = self.accessDetailsFormatter(accessRequestToBeApproved["accessType"])
        FileUserAccessObject.accessId = PermissionsAssignedObject.query.filter_by(**accessDetails).first().id
        UserObject.name = userName
        FileUserAccessObject.user = UserObject
        accessingUsersOfGivenFileData.users.append(FileUserAccessObject)
        return accessingUsersOfGivenFileData

    def getFilesObjectForspecificUser(self, ownerName):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        ownerDetails = OwnerObject.query.filter_by(name=ownerName).first()
        return FileObject.query.filter_by(ownerId=ownerDetails.id).all()

    def getOwnerDetails(self, ownerId):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        return OwnerObject.query.filter_by(id=ownerId).first()

    def listAllFileAccessDetails(self):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        return FileObject.query.all()

    def getAccessDetailOfFile(self, fileName):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        return FileObject.query.filter_by(name=fileName).first()
