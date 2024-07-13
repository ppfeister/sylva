from .modules import proxynova
from .collector import Collector

class Handler:
    def __init__(self):
        self.collector:Collector = Collector()
    def search_all(self, query:str):
        _proxynova = proxynova.ProxyNova(collector=self.collector)
        _proxynova.search(query)
