from AccessManagementService.PostgresCommunicator.Models import ModelFactory


class PostgresReadTaskHandler:
    def __init__(self, modelInstance, databseInstance):
        self.modelInstance = modelInstance
        self.databseInstance = databseInstance

    def accessDetailsForParticularFileUserFormatter(self, AccessDetailsForFile, fileUserRecord):
        AccessDetailsForFile = AccessDetailsForFile.__dict__
        fileUserRecord["access"] = ""
        if AccessDetailsForFile["read"] == True: fileUserRecord["access"] = fileUserRecord["access"] + "read "
        if AccessDetailsForFile["write"] == True: fileUserRecord["access"] = fileUserRecord["access"] + "write "
        if AccessDetailsForFile["delete"] == True: fileUserRecord["access"] = fileUserRecord["access"] + "delete"

    def getFilesInformationForSpecificUser(self, ownerName):
        fileObjects = ModelFactory.ModelFactory(self.modelInstance, self.databseInstance).getFilesObjectForspecificUser(
            ownerName)
        filesOfTheUserAccessesByOthers = []
        for eachFileObject in fileObjects:
            fileUserRecord = {}
            fileUserRecord["file"] = eachFileObject.name
            for eachUser in eachFileObject.users:
                if (eachUser.user.name != ownerName):
                    fileUserRecord["name"] = eachUser.user.name
                    fileUserRecord["access"] = self.accessDetailsForParticularFileUserFormatter(eachUser.accessGiven,
                                                                                                fileUserRecord[
                                                                                                    "access"])
                    filesOfTheUserAccessesByOthers.append(fileUserRecord)
        return filesOfTheUserAccessesByOthers

    def accessRequestsListFormatter(self, accessRequestsList):
        accessRequestsOfTheUserOrOwnerFormattedList = []
        for eachAccessRequestObject in accessRequestsList:
            eachAccessRequestObject = eachAccessRequestObject.__dict__
            del eachAccessRequestObject["id"]
            del eachAccessRequestObject["_sa_instance_state"]
            accessRequestsOfTheUserOrOwnerFormattedList.append(eachAccessRequestObject)
        return accessRequestsOfTheUserOrOwnerFormattedList

    def getAccessRequestsCreatedByTheUser(self, userName):
        accessRequestsOfTheUserList = ModelFactory.ModelFactory(self.modelInstance,
                                                                self.databseInstance).getAccessRequestsOfTheUser(
            userName)
        return self.accessRequestsListFormatter(accessRequestsOfTheUserList)

    def getAccessRequestsForOwnerToApproval(self, ownerName):
        accessRequestsOfTheOwnerList = ModelFactory.ModelFactory(self.modelInstance,
                                                                 self.databseInstance).getAccessRequestsOfTheUser(
            ownerName)
        return self.accessRequestsListFormatter(accessRequestsOfTheOwnerList)
