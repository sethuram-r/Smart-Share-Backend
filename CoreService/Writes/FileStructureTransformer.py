from CoreService import logging


class FileStructureTransformer:

    def _filterValidS3Result(self, validS3Result):

        filteredResult = [eachContent["Key"] for eachContent in validS3Result["Contents"]]
        return filteredResult

    def _isInputValid(self, s3ResultToBeTransformed):

        if "Contents" not in s3ResultToBeTransformed:
            return False
        else:
            return True

    def transformationProcessPipeline(self, s3ResultToBeTransformed):

        logging.info("Inside transformationProcessPipeline")

        validInput = self._isInputValid(s3ResultToBeTransformed)
        if validInput == False:
            return None
        else:
            filteredResult = self._filterValidS3Result(s3ResultToBeTransformed)
            return filteredResult

    def extractFileNamesForDeleteOperation(self, selectedFiles):

        logging.info("Inside extractFileNamesForSavepointCreationInDeleteOperation")

        return [eachselectedFile["Key"] for eachselectedFile in selectedFiles]

    def extractFolderNameForSavepointCreationInDeleteOperation(self, filesToBeDeleted):
        if len(filesToBeDeleted) == 1:
            fileToBeDeleted = filesToBeDeleted[0]
            fileToBeDeleted = fileToBeDeleted.split("/")
            del fileToBeDeleted[len(fileToBeDeleted) - 1]
            folderName = "/".join(fileToBeDeleted)
            return folderName
        else:
            rootFolder = filesToBeDeleted[0]
            return rootFolder
