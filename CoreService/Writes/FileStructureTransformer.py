""" This class transforms the results from the data source to a hierarchical structure. """


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
        validInput = self._isInputValid(s3ResultToBeTransformed)
        if validInput == False:
            return None
        else:
            filteredResult = self._filterValidS3Result(s3ResultToBeTransformed)
            return filteredResult
