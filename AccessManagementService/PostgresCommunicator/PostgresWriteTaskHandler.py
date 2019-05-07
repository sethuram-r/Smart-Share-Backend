from AccessManagementService import databaseInstance
from AccessManagementService.PostgresCommunicator.Models import ModelFactory
from AccessManagementService.PostgresCommunicator.RequestToObjectMappers import RequestToDatabaseObjectMapper


class PostgresWriteTaskHandler:

    def __init__(self, modelInstance=None, databseInstance=None):
        self.modelInstance = modelInstance
        self.databseInstance = databseInstance

    def createAccessRequest(self, accessRequest):

        accessRequestObject = ModelFactory.ModelFactory().getAccessRequestObject()
        requestMappedAccessRequestObject = RequestToDatabaseObjectMapper.RequestToDatabaseObjectMapper().RequestMappedAccessRequestObject(
            accessRequestObject, accessRequest)

        try:
            databaseInstance.session.add(requestMappedAccessRequestObject)
            databaseInstance.session.commit()
            print("Access Request has been successfully created")  # logger implementation
        except:
            print("Failed to create Access Request")

    def addUserToFileAccessingUserList(self, accessRequestToBeApproved):

        fileUserAccessObjectForGivenFileAndOwner = ModelFactory.ModelFactory().getFileAndItsAccessingUsersObjectForExistingFile(
            accessRequestToBeApproved)

        try:
            databaseInstance.session.add(fileUserAccessObjectForGivenFileAndOwner)
            databaseInstance.session.commit()
            print("Access Request has been successfully added to the existing file")  # logger implementation
        except:
            print("Access Request has not been successfully added to the existing file")



    def approveAccessRequest(self, accessRequestToBeApproved):

        accessRequestForWhichStatusHasToBeApproved = ModelFactory.ModelFactory().getAccessRequestObjectToBeDeletedOrApprovedOrRejected(
            accessRequestToBeApproved)
        if accessRequestForWhichStatusHasToBeApproved is not None and accessRequestForWhichStatusHasToBeApproved.statusOfRequest == "ongoing":
            accessRequestForWhichStatusHasToBeApproved.statusOfRequest = "approved"
            try:
                databaseInstance.session.add(accessRequestForWhichStatusHasToBeApproved)
                databaseInstance.session.commit()
                print("Access Request has been successfully approved")  # logger implementation
                self.addUserToFileAccessingUserList(accessRequestToBeApproved)
            except:
                print("Failed to approve Access Request")


    def rejectAccessRequest(self, accessRequestToBeRejected):

        accessRequestForWhichStatusHasToBeRejected = ModelFactory.ModelFactory().getAccessRequestObjectToBeDeletedOrApprovedOrRejected(
            accessRequestToBeRejected)
        if accessRequestForWhichStatusHasToBeRejected is not None and accessRequestForWhichStatusHasToBeRejected.statusOfRequest == "ongoing":
            accessRequestForWhichStatusHasToBeRejected.statusOfRequest = "rejected"
            try:
                databaseInstance.session.add(accessRequestForWhichStatusHasToBeRejected)
                databaseInstance.session.commit()
                print("Access Request has been successfully rejected")  # logger implementation
            except:
                print("Failed to reject Access Request")


    def deleteAccessRequestRecord(self, accessRequestToBeDeleted):
        accessRequestObjectToBeDeleted = ModelFactory.ModelFactory().getAccessRequestObjectToBeDeletedOrApprovedOrRejected(
            accessRequestToBeDeleted)
        try:
            databaseInstance.session.delete(accessRequestObjectToBeDeleted)
            databaseInstance.session.commit()
            print("Access Request has been successfully deleted")  # logger implementation
        except:
            print('Warning deleteAccessRequest Error in Deletion')

    def deleteAccessDetailForFiles(self, FilesForCorrespondingAccessRecordsToBeDeleted):
        resultOfDeleteOperation = []
        for eachFile in FilesForCorrespondingAccessRecordsToBeDeleted:
            fileObject = ModelFactory.ModelFactory(self.modelInstance,
                                                   self.databseInstance).getAccessDetailOfFile(eachFile["Key"])

            try:
                databaseInstance.session.delete(fileObject)
                databaseInstance.session.commit()
                resultOfDeleteOperation.append(True)
            except:
                print("Error in deleting Access Details ")
                resultOfDeleteOperation.append(False)

        if False not in resultOfDeleteOperation:
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
