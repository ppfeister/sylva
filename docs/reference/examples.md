```python
from sylva.handler import Handler

handler = Handler()
handler.branch_all('username')
results = handler.collector.get_data() #(1)!

print(results)
```

1.  [Handler][sylva.handler.Handler]'s member collector is a [sylva.Collector][] object where method get_data() returns a [pandas.DataFrame][]{target="_blank"}


```python
from sylva.handler import Handler, QueryDataItem
from sylva.types import QueryType

handler = Handler()

query = QueryDataItem(query='username', type=QueryType.USERNAME)
handler.branch_all(query)
results = handler.collector.get_data() #(1)!

print(results)
```

1.  [Handler][sylva.handler.Handler]'s member collector is a [sylva.Collector][] object where method get_data() returns a [pandas.DataFrame][]{target="_blank"}
