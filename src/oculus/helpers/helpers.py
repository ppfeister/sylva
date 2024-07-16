import pandas as pd

class RequestError(Exception):
    pass
class IncompatibleQueryType(Exception):
    pass
class APIKeyError(Exception):
    def __init__(self, message:str=None, key_not_provided:bool=False):
        super().__init__(message)
        self.key_not_provided = key_not_provided

class ResultDataFrame:
    def __init__(self):
        self.data = pd.DataFrame(
            columns=[
                'query',
                'source_name',
                'spider_recommended',
                'platform_name',
                'platform_url',
                'username',
                'email',
                'phone',
                'password',
                'age',
                'sex',
                'first_name',
                'middle_name',
                'last_name',
                'full_name',
                'birth_date',
                'street',
                'unit',
                'city',
                'region',
                'postal_code',
                'country',
                'raw_address',
                'comment',
                ]
        )
    def __str__(self) -> str:
        return self.data.__str__()
    def insert_raw(
            self,
            query:str,
            source_name:str,
            spider_recommended:str = None,
            platform_name:str = None,
            platform_url:str = None,
            username:str = None,
            email:str = None,
            phone:str = None,
            password:str = None,
            age:int = None,
            sex:str = None,
            first_name:str = None,
            middle_name:str = None,
            last_name:str = None,
            birth_date:str = None,
            street:str = None,
            unit:str = None,
            city:str = None,
            region:str = None,
            postal_code:str = None,
            country:str = None,
    ) -> pd.DataFrame:
        new_data = pd.DataFrame([{
            'query': query,
            'source_name': source_name,
            'spider_recommended': spider_recommended,
            'platform_name': platform_name,
            'platform_url': platform_url,
            'username': username,
            'email': email,
            'phone': phone,
            'password': password,
            'age': age,
            'sex': sex,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'birth_date': birth_date,
            'street': street,
            'unit': unit,
            'city': city,
            'region': region,
            'postal_code': postal_code,
            'country': country,
        }])
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        return self.data
    def insert_frame(self, new_data:pd.DataFrame) -> pd.DataFrame:
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        return self.data
    def get_data(self) -> pd.DataFrame:
        return self.data
