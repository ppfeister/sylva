class RequestError(Exception):
    """Raised when a request fails within a module"""
    def __init__(
        self,
        message:str='',
        rate_limit_exceeded:bool=False,
    ):
        super().__init__(message)
        self.rate_limit_exceeded = rate_limit_exceeded

class IncompatibleQueryType(Exception):
    pass

class APIKeyError(Exception):
    """Raised for issues relating to the use of third-party API keys"""
    def __init__(self, message:str='', key_not_provided:bool=False):
        super().__init__(message)
        self.key_not_provided = key_not_provided
