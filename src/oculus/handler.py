from .collector import Collector
from .modules import (
    endato,
    proxynova,
)


class Handler:
    def __init__(self):
        self.collector:Collector = Collector()
    def search_all(self, query:str):
        _proxynova = proxynova.ProxyNova(collector=self.collector)
        _proxynova.search(query)
        _endato = endato.Endato(collector=self.collector)
        _endato.search(query)
