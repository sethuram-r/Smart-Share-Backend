from AccessManagementService.PostgresCommunicator.Models import ModelFactory
from AccessManagementService.PostgresCommunicator.RequestToObjectMappers import RequestToDatabaseObjectMapper


class PostgresWriteTaskHandler:

    def __init__(self, modelInstance, databseInstance):
        self.modelInstance = modelInstance
        self.databseInstance = databseInstance

    def createAccessRequest(self, accessRequest):

        accessRequestObject = ModelFactory.ModelFactory(self.modelInstance,
                                                        self.databseInstance).getAccessRequestObject()
        requestMappedAccessRequestObject = RequestToDatabaseObjectMapper.RequestToDatabaseObjectMapper().RequestMappedAccessRequestObject(
            accessRequestObject, accessRequest)
        self.databseInstance.session.add(requestMappedAccessRequestObject)
        commitedId = self.databseInstance.session.commit()  # this returns id if the transaction is commited
        if commitedId == None: print('Warning createAccessRequest Error in Insertion')  # logger implementation

    def approveAccessRequest(self, accessRequestToBeApproved):
        accessRequestObject = ModelFactory.ModelFactory(self.modelInstance,
                                                        self.databseInstance).getAccessRequestObject()
        accessRequestForWhichStatusHasToBeApproved = accessRequestObject.query.filter_by(
            file=accessRequestToBeApproved["file"], ownerOfFile=accessRequestToBeApproved["owner"]).all()
        print("accessRequestForWhichStatusHasToBeApproved-------->", accessRequestForWhichStatusHasToBeApproved)
        accessRequestForWhichStatusHasToBeApproved.statusOfRequest = "approved"
        self.databseInstance.session.add(accessRequestForWhichStatusHasToBeApproved)
        commitedId = self.databseInstance.session.commit()  ## unsure whether it works or not
        if commitedId != None:
            fileUserAccessObjectForGivenFileAndOwner = ModelFactory.ModelFactory(self.modelInstance,
                                                                                 self.databseInstance).getFileAndItsAccessingUsersObjectForExistingFile(
                accessRequestToBeApproved)
            self.databseInstance.session.add(fileUserAccessObjectForGivenFileAndOwner)
            commitedId = self.databseInstance.session.commit()  # this returns id if the transaction is commited
            if commitedId == None: print('Warning approveAccessRequest Error in Insertion')  # logger implementation

    def rejectAccessRequest(self, accessRequestToBeRejected):
        accessRequestObject = ModelFactory.ModelFactory(self.modelInstance,
                                                        self.databseInstance).getAccessRequestObject()
        accessRequestForWhichStatusHasToBeRejected = accessRequestObject.query.filter_by(
            file=accessRequestToBeRejected["file"], ownerOfFile=accessRequestToBeRejected["owner"]).all()
        print("accessRequestForWhichStatusHasToBeRejected-------->", accessRequestForWhichStatusHasToBeRejected)
        accessRequestForWhichStatusHasToBeRejected.statusOfRequest = "rejected"
        self.databseInstance.session.add(accessRequestForWhichStatusHasToBeRejected)
        commitedId = self.databseInstance.session.commit()
        if commitedId == None: print('Warning rejectAccessRequest Error in Insertion')  # logger implementation

    def deleteAccessRequestRecord(self, accessRequestToBeDeleted):
        accessRequestObject = ModelFactory.ModelFactory(self.modelInstance,
                                                        self.databseInstance).getAccessRequestObject()
        requestMappedAccessRequestObject = RequestToDatabaseObjectMapper.RequestToDatabaseObjectMapper().RequestMappedAccessRequestObjectForDelete(
            accessRequestObject,
            accessRequestToBeDeleted)  ### have to check whether its needed or not if not the request can be diretly sennt to db
        self.databseInstance.session.delete(requestMappedAccessRequestObject)
        commitedId = self.databseInstance.session.commit()  # this returns id if the transaction is commited
        if commitedId == None: print('Warning deleteAccessRequest Error in Deletion')

    def deleteAccessDetailForFiles(self, FilesForCorrespondingAccessRecordsToBeDeleted):
        resultOfDeleteOperation = []
        for eachFile in FilesForCorrespondingAccessRecordsToBeDeleted:
            fileObject = ModelFactory.ModelFactory(self.modelInstance,
                                                   self.databseInstance).getAccessDetailOfFile(eachFile)
            self.databseInstance.session.delete(fileObject)
            resultOfDeleteOperation.append(self.databseInstance.session.commit())
        if None not in resultOfDeleteOperation:
            return ({"status": True})
        else:
            return ({"status": False})

    def createUserAccessDetailForFile(self, accessDetailsToBeInserted):

        numberOfAccessingUsers = len(accessDetailsToBeInserted["accessing_users"])
        newFileObject = ModelFactory.ModelFactory(self.modelInstance,
                                                  self.databseInstance).getFileAndItsAccessingUsersObjectForNonExistingFile(
            numberOfAccessingUsers)

        mappedNewFileObject = RequestToDatabaseObjectMapper.RequestToDatabaseObjectMapper().userAccessDetailToCorrespondingObect(
            newFileObject, accessDetailsToBeInserted)
        self.databseInstance.session.add(mappedNewFileObject)
        commitedId = self.databseInstance.session.commit()
        if commitedId == None:
            return ({"status": True})
        else:
            return ({"status": False})
