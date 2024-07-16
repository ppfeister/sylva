import pandas as pd

class RequestError(Exception):
    pass

class IncompatibleQueryType(Exception):
    pass

class APIKeyError(Exception):
    def __init__(self, message: str = None, key_not_provided: bool = False):
        super().__init__(message)
        self.key_not_provided = key_not_provided

class ResultDataFrame:
    def __init__(self):
        columns = [
            'query', 'source_name', 'spider_recommended', 'platform_name', 'platform_url', 
            'username', 'email', 'phone', 'password', 'age', 'sex', 'first_name', 
            'middle_name', 'last_name', 'full_name', 'birth_date', 'street', 'unit', 
            'city', 'region', 'postal_code', 'country', 'raw_address', 'comment'
        ]
        self.data = pd.DataFrame(columns=columns)

    def __str__(self) -> str:
        return str(self.data)

    def insert_raw(self, **kwargs) -> pd.DataFrame:
        new_data = pd.DataFrame([kwargs])
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        return self.data

    def insert_frame(self, new_data: pd.DataFrame) -> pd.DataFrame:
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        return self.data

    def get_data(self) -> pd.DataFrame:
        return self.data
