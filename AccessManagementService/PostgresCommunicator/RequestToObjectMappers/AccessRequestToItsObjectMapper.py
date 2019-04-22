class AccessRequestToItsObjectMapper:

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
