from .collector import Collector
from .helpers.helpers import RequestError
from .integrations import (
    endato,
    proxynova,
    intelx,
)


class Handler:
    def __init__(self):
        self.collector:Collector = Collector()
    def search_all(self, query:str):
        try:
            _proxynova = proxynova.ProxyNova(collector=self.collector)
            _proxynova.search(query=query)
        except RequestError:
            pass
        try:
            _endato = endato.Endato(collector=self.collector)
            _endato.search(query=query)
        except RequestError:
            pass
        #try:
        #    _intelx = intelx.IntelX(collector=self.collector)
        #    _intelx.search(query=query)
        #except RequestError:
        #    pass
