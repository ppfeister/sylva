class RequestError(Exception):
    pass

class IncompatibleQueryType(Exception):
    pass

class APIKeyError(Exception):
    def __init__(self, message:str=None, key_not_provided:bool=False):
        super().__init__(message)
        self.key_not_provided = key_not_provided
