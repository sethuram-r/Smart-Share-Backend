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
                    self.accessDetailsForParticularFileUserFormatter(eachUser.accessGiven, fileUserRecord)
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

    def getOwnerDetailsForFile(self, ownerId):
        return ModelFactory.ModelFactory(self.modelInstance,
                                         self.databseInstance).getOwnerDetails(ownerId).__dict__["name"]

    def fileObjectsFormatToDictionaries(self, listOfFileObjects):
        listOfFileObjectsInDictionaryFormat = []
        for eachFileObject in listOfFileObjects:
            eachFileDict = {}
            eachFileDict["file"] = eachFileObject.name
            eachFileDict["owner"] = self.getOwnerDetailsForFile(eachFileObject.ownerId)
            eachFileDict["accessingUsers"] = []
            for eachUser in eachFileObject.users:
                user = {}
                user["name"] = eachUser.user.name
                user["read"] = eachUser.accessGiven.__dict__["read"]
                user["write"] = eachUser.accessGiven.__dict__["write"]
                user["delete"] = eachUser.accessGiven.__dict__["delete"]
                eachFileDict["accessingUsers"].append(user)
            listOfFileObjectsInDictionaryFormat.append(eachFileDict)
        return listOfFileObjectsInDictionaryFormat

    def fetchUserAcessDataForFilesandFoldersInDictionaryFormat(self):
        listOfFileObjects = ModelFactory.ModelFactory(self.modelInstance,
                                                      self.databseInstance).listAllFileAccessDetails()
        listOfFileObjectsInDictionaryFormat = self.fileObjectsFormatToDictionaries(listOfFileObjects)
        return listOfFileObjectsInDictionaryFormat

    def fileObjectFormatToDictionary(self, fileObject):
        fileDict = {}
        fileDict["file"] = fileObject.name
        fileDict["owner"] = self.getOwnerDetailsForFile(fileObject.ownerId)
        fileDict["accessingUsers"] = []
        for eachUser in fileObject.users:
            user = {}
            user["name"] = eachUser.user.name
            user["read"] = eachUser.accessGiven.__dict__["read"]
            user["write"] = eachUser.accessGiven.__dict__["write"]
            user["delete"] = eachUser.accessGiven.__dict__["delete"]
            fileDict["accessingUsers"].append(user)
        return fileDict

    def fetchUserAcessDataForSingleFileOrFolderInDictionaryFormat(self, fileName):
        fileObject = ModelFactory.ModelFactory(self.modelInstance,
                                               self.databseInstance).getAccessDetailOfFile(fileName)
        fileObjectInDictionaryFormat = self.fileObjectFormatToDictionary(fileObject)

        return fileObjectInDictionaryFormat
