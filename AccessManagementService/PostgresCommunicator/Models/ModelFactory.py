class ModelFactory:

    def __init__(self, model, db):
        self.model = model
        self.db = db

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

        class Owner(self.model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.Text)
            files = self.db.relationship('File', backref='owner', lazy=True)

        class File(self.model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.Text)
            ownerId = self.db.Column(self.db.Integer, self.db.ForeignKey('owner.id'))
            owner = self.db.relationship("Owner")  ### added apart from tested sample
            users = self.db.relationship("FileUserAccess", backref="file")

        class FileUserAccess(self.model):
            fileId = self.db.Column(self.db.Integer, self.db.ForeignKey('file.id'), primary_key=True)
            userId = self.db.Column(self.db.Integer, self.db.ForeignKey('user.id'), primary_key=True)
            accessId = self.db.Column(self.db.Integer, self.db.ForeignKey('permissions_assigned.id'))
            accessGiven = self.db.relationship('PermissionsAssigned')

        class User(self.model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.Text)
            files = self.db.relationship("FileUserAccess", backref="user")

        class PermissionsAssigned(self.model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            read = self.db.Column(self.db.Boolean)
            write = self.db.Column(self.db.Boolean)
            delete = self.db.Column(self.db.Boolean)

            def __repr__(self):
                return '<PermissionsAssigned %r %r %r>' % (
                    self.read, self.write, self.delete)

        return (Owner(), File(), FileUserAccess(), PermissionsAssigned(), User())

    def getFileAndItsAccessingUsersObject(self, numberOfAccessingUsers):

        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        file = FileObject
        file.owner = OwnerObject
        for fileUserAccessAssociationObject in range(numberOfAccessingUsers):
            fileUserAccessAssociationObject = FileUserAccessObject
            fileUserAccessAssociationObject.accessId = PermissionsAssignedObject
            fileUserAccessAssociationObject.user = UserObject
            file.users.append(fileUserAccessAssociationObject)

        ### Object implemenatation Example

        # file.name = "samp.text"
        # file.owner.name = "xaviers"
        # for each_user in file.users:
        #     each_user.access_id = each_user.access_id.query.filter_by(read=True, write=True, delete=False).first().id
        #     each_user.user.name = "reddyser"
        #
        # db.session.add(file)
        # db.session.commit()

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

        # print(accessing_users.users)
        # for user in accessing_users.users:
        #     print(user.user.name)
        #     print(user.access_given)

        ### Implementation
        # file_user_assoc = FileUserAccess()
        # file_user_assoc.access_given = PermissionsAssigned(read=True,write=True,delete=False)
        # file_user_assoc.user = User(name = "ramu kaka")
        # accessing_users.users.append(file_user_assoc)
        #
        # db.session.add(accessing_users)
        # db.session.commit()

        return accessingUsersOfGivenFileData

    def getFilesObjectForspecificUser(self, ownerName):

        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        ownerDetails = OwnerObject.query.filter_by(name=ownerName).first()
        return FileObject.query.filter_by(ownerId=ownerDetails.id).all()

    def getOwnerDetails(self, ownerId):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        return OwnerObject.query.filter_by(ownerId=ownerId).first()

    def listAllFileAccessDetails(self):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        return FileObject.query.all()

    def getAccessDetailOfFile(self, fileName):
        OwnerObject, FileObject, FileUserAccessObject, PermissionsAssignedObject, UserObject = self.getFileAndItsAccessingUsersModel()
        return FileObject.query.filter_by(name=fileName)
