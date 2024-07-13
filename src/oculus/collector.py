from .helpers.helpers import ResultDataFrame

class Collector:
    def __init__(self):
        self.data:ResultDataFrame = ResultDataFrame()
    def insert(self, new_data:ResultDataFrame):
        self.data.insert_frame(new_data)
    def get_data(self):
        return self.data