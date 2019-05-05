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
        doesOwnerExists = userAccessForFileObject.owner.query.filter_by(
            name=userAccessForFileToBeMapped["owner"]).first()
        if doesOwnerExists is None:
            userAccessForFileObject.owner.name = userAccessForFileToBeMapped["owner"]
        else:
            userAccessForFileObject.ownerId = doesOwnerExists.id
            del userAccessForFileObject.owner

        for eachUserInfo in userAccessForFileToBeMapped["accessing_users"]:
            for eachUserObject in userAccessForFileObject.users:
                eachUserObject.accessId = eachUserObject.accessId.query.filter_by(read=eachUserInfo["read"],
                                                                                  write=eachUserInfo["write"],
                                                                                  delete=eachUserInfo[
                                                                                      "delete"]).first().id

                print("name-------->", userAccessForFileToBeMapped["owner"])
                doesUserExists = eachUserObject.user.query.filter_by(name=userAccessForFileToBeMapped["owner"]).first()
                if doesUserExists is None:
                    eachUserObject.user.name = eachUserInfo["name"]
                else:
                    eachUserObject.userId = doesUserExists.id
                    del eachUserObject.user
        return userAccessForFileObject
