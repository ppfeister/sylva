from typing import List

from .collector import Collector
from .helpers.helpers import RequestError, APIKeyError
from .integrations import (
    endato,
    proxynova,
    intelx,
)
from .modules import (
    pgp as pgp_module,
)


class Handler:
    def __init__(self):
        self.collector:Collector = Collector()
        self.runners:List = [
            proxynova.ProxyNova(collector=self.collector),
            endato.Endato(collector=self.collector),
            intelx.IntelX(collector=self.collector),
            pgp_module.PGPModule(collector=self.collector),
        ]
    def search_all(self, query:str):
        for runner in self.runners:
            try:
                runner.search(query=query)
            except RequestError:
                pass
            except APIKeyError as e:
                if e.key_not_provided:
                    print(f'API key for {runner.source_name} not provided. Please add it to your config.')
