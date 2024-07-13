import pandas as pd

class Collector:
    def __init__(self):
        #data = pd.DataFrame(columns=['source', 'source_name', 'description', 'spider_recommended', 'results'])
        self.data = pd.DataFrame(columns=[
            'query',
            'source_name',
            'source_description',
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
            'birth_date',
            'street',
            'unit',
            'city',
            'state',
            'zip',
            ])
    def insert(self, new_data:pd.DataFrame):
        self.data = pd.concat([self.data, new_data], ignore_index=True)
    def get_data(self):
        return self.data