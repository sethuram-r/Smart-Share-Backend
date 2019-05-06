from AccessManagementService.PostgresCommunicator.Models import ObjectRelationalModel


class ModelFactory:

    def __init__(self, model, db):
        self.model = model
        self.db = db

        self.objectRelationalModel = ObjectRelationalModel.ObjectRelationalModel()

    def getAccessRequestObject(self):
        class AccessRequest(self.model):
            # id  = self.db.Column(self.db.Integer, primary_key=True)  # not need
            file = self.db.Column(self.db.String(100), nullable=False)
            ownerOfFile = self.db.Column(self.db.String(100), nullable=False)
            userName = self.db.Column(self.db.String(100), nullable=False)
            accessType = self.db.Column(self.db.String(100), nullable=False)
            statusOfRequest = self.db.Column(self.db.String(100), nullable=False)

            def __repr__(self):
                return '<AccessRequest %r %r %r %r %r %r>' % (
                self.id, self.file, self.ownerOfFile, self.username, self.accessType, self.statusOfRequest)

        return AccessRequest()

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
        accessRecord = existingAccess.__dict__
        del accessRecord["id"]
        del accessRecord["_sa_instance_state"]
        accessRecord[accessToUpdate] = True
        return accessRecord

    def getFileAndItsAccessingUsersObjectForExistingFile(self, accessRequestToBeApproved):

        fileName = accessRequestToBeApproved["file"]
        ownerName = accessRequestToBeApproved["owner"]
        userName = accessRequestToBeApproved["username"]

        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()

        ownerData = OwnerObject.query.filter_by(name=ownerName).first()
        accessingUsersOfGivenFileData = FileObject.query.filter_by(name=fileName, owner_id=ownerData.id).first()

        for eachFileUserAssoc in accessingUsersOfGivenFileData.users:
            if eachFileUserAssoc.user.name == userName:
                accessDetails = self.accessDetailsToBeUpdatedForThatUser(eachFileUserAssoc.accessGiven,
                                                                         accessRequestToBeApproved["access"])
                eachFileUserAssoc.access_id = PermissionsAssignedObject.query.filter_by(**accessDetails).first().id
                return accessingUsersOfGivenFileData  ### unsure

        accessDetails = self.accessDetailsFormatter(accessRequestToBeApproved["access"])
        FileUserAccessObject.access_id = PermissionsAssignedObject.query.filter_by(**accessDetails).first().id
        UserObject.name = userName
        FileUserAccessObject.user = UserObject
        accessingUsersOfGivenFileData.append(FileUserAccessObject)
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
