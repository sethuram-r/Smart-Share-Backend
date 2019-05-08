from AccessManagementService import databaseInstance, logging
from AccessManagementService.PostgresCommunicator.Models import ModelFactory
from AccessManagementService.PostgresCommunicator.RequestToObjectMappers import RequestToDatabaseObjectMapper


class PostgresWriteTaskHandler:

    def __init__(self, modelInstance=None, databseInstance=None):
        self.modelInstance = modelInstance
        self.databseInstance = databseInstance

    def createAccessRequest(self, accessRequest):

        logging.info("Inside createAccessRequest")

        accessRequestObject = ModelFactory.ModelFactory().getAccessRequestObject()
        requestMappedAccessRequestObject = RequestToDatabaseObjectMapper.RequestToDatabaseObjectMapper().RequestMappedAccessRequestObject(
            accessRequestObject, accessRequest)

        try:
            databaseInstance.session.add(requestMappedAccessRequestObject)
            databaseInstance.session.commit()
            logging.info("Access Request has been successfully created")
        except:
            logging.warning("Failed to create Access Request")

    def addUserToFileAccessingUserList(self, accessRequestToBeApproved):

        logging.info("Inside addUserToFileAccessingUserList")

        fileUserAccessObjectForGivenFileAndOwner = ModelFactory.ModelFactory().getFileAndItsAccessingUsersObjectForExistingFile(
            accessRequestToBeApproved)

        try:
            databaseInstance.session.add(fileUserAccessObjectForGivenFileAndOwner)
            databaseInstance.session.commit()
            logging.info("Access Request has been successfully added to the existing file")
        except:
            logging.warning("Access Request has not been successfully added to the existing file")



    def approveAccessRequest(self, accessRequestToBeApproved):

        logging.info("Inside approveAccessRequest")

        accessRequestForWhichStatusHasToBeApproved = ModelFactory.ModelFactory().getAccessRequestObjectToBeDeletedOrApprovedOrRejected(
            accessRequestToBeApproved)
        if accessRequestForWhichStatusHasToBeApproved is not None and accessRequestForWhichStatusHasToBeApproved.statusOfRequest == "ongoing":
            accessRequestForWhichStatusHasToBeApproved.statusOfRequest = "approved"
            try:
                databaseInstance.session.add(accessRequestForWhichStatusHasToBeApproved)
                databaseInstance.session.commit()
                logging.info("Access Request has been successfully approved")
                self.addUserToFileAccessingUserList(accessRequestToBeApproved)
            except:
                logging.warning("Failed to approve Access Request")


    def rejectAccessRequest(self, accessRequestToBeRejected):

        logging.info("Inside rejectAccessRequest")

        accessRequestForWhichStatusHasToBeRejected = ModelFactory.ModelFactory().getAccessRequestObjectToBeDeletedOrApprovedOrRejected(
            accessRequestToBeRejected)
        if accessRequestForWhichStatusHasToBeRejected is not None and accessRequestForWhichStatusHasToBeRejected.statusOfRequest == "ongoing":
            accessRequestForWhichStatusHasToBeRejected.statusOfRequest = "rejected"
            try:
                databaseInstance.session.add(accessRequestForWhichStatusHasToBeRejected)
                databaseInstance.session.commit()
                logging.info("Access Request has been successfully rejected")
            except:
                logging.warning("Failed to reject Access Request")


    def deleteAccessRequestRecord(self, accessRequestToBeDeleted):

        logging.info("Inside deleteAccessRequestRecord")

        accessRequestObjectToBeDeleted = ModelFactory.ModelFactory().getAccessRequestObjectToBeDeletedOrApprovedOrRejected(
            accessRequestToBeDeleted)
        try:
            databaseInstance.session.delete(accessRequestObjectToBeDeleted)
            databaseInstance.session.commit()
            logging.info("Access Request has been successfully deleted")
        except:
            logging.warning("Failed to delete Access Request")


    def deleteAccessDetailForFiles(self, FilesForCorrespondingAccessRecordsToBeDeleted):

        logging.info("Inside deleteAccessDetailForFiles")

        resultOfDeleteOperation = []
        for eachFile in FilesForCorrespondingAccessRecordsToBeDeleted:
            fileObject = ModelFactory.ModelFactory(self.modelInstance,
                                                   self.databseInstance).getAccessDetailOfFile(eachFile["Key"])
            try:
                databaseInstance.session.delete(fileObject)
                databaseInstance.session.commit()
                resultOfDeleteOperation.append(True)
            except:
                resultOfDeleteOperation.append(False)

        if False not in resultOfDeleteOperation:
            logging.info("Access Details for files have been deleted")
            return ({"status": True})
        else:
            logging.warning("Error in deleting Access Details for files")
            return ({"status": False})

    def createUserAccessDetailForFile(self, accessDetailsToBeInserted):

        logging.info("Inside createUserAccessDetailForFile")

        numberOfAccessingUsers = len(accessDetailsToBeInserted["accessing_users"])
        newFileObject = ModelFactory.ModelFactory(self.modelInstance,
                                                  self.databseInstance).getFileAndItsAccessingUsersObjectForNonExistingFile(
            numberOfAccessingUsers)

        mappedNewFileObject = RequestToDatabaseObjectMapper.RequestToDatabaseObjectMapper().userAccessDetailToCorrespondingObect(
            newFileObject, accessDetailsToBeInserted)

        try:
            databaseInstance.session.add(mappedNewFileObject)
            databaseInstance.session.commit()
            logging.info("Access Details for files have been created")
            return ({"status": True})
        except:
            logging.warning("Error in creating Access Details for files")
            return ({"status": False})

