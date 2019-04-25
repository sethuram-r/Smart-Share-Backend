class RequestToDatabaseObjectMapper:

    def RequestMappedAccessRequestObject(self, accessRequestObjectForMapping, accessRequestToBeMapped):
        accessRequestObjectForMapping.file = accessRequestToBeMapped["path"]
        accessRequestObjectForMapping.username = accessRequestToBeMapped["username"]
        accessRequestObjectForMapping.ownerOfFile = accessRequestToBeMapped["owner"]
        accessRequestObjectForMapping.accessType = accessRequestToBeMapped["access"]
        accessRequestObjectForMapping.statusOfRequest = "ongoing"
        return accessRequestObjectForMapping

    def RequestMappedAccessRequestObjectForDelete(self, accessRequestObjectForMapping, accessRequestToBeMapped):
        accessRequestObjectForMapping.file = accessRequestToBeMapped["path"]
        accessRequestObjectForMapping.username = accessRequestToBeMapped["username"]
        accessRequestObjectForMapping.ownerOfFile = accessRequestToBeMapped["ownerOfFile"]
        accessRequestObjectForMapping.accessType = accessRequestToBeMapped["accessType"]
        accessRequestObjectForMapping.statusOfRequest = accessRequestToBeMapped["statusOfRequest"]
        return accessRequestObjectForMapping

    def userAccessDetailToCorrespondingObect(self, userAccessForFileObject, userAccessForFileToBeMapped):
        userAccessForFileObject.name = userAccessForFileToBeMapped["file"]
        userAccessForFileObject.owner.name = userAccessForFileToBeMapped["owner"]

        for eachUser in range(len(userAccessForFileToBeMapped["accessing_users"])):
            accessingUserOfFile = userAccessForFileToBeMapped["accessing_users"][eachUser]
            accessingUserOfFileObject = userAccessForFileObject.users[eachUser]
            accessingUserOfFileObject.accessId = accessingUserOfFileObject.accessId.query.filter_by(
                read=accessingUserOfFile["read"], write=accessingUserOfFile["write"]
                , delete=accessingUserOfFile["delete"])
            accessingUserOfFileObject.user.name = accessingUserOfFile["name"]

        return userAccessForFileObject
