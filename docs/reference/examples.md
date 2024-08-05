Sylva exposes a relatively simple API for programmatic use and for easier inclusion in downstream projects.
There are two primary methods of use: one that searches based on a generic and arbitrary string, and one
that conducts a more targeted search based on the type of data provided. In either case, methods
[branch_all][sylva.handler.Handler.branch_all] and [search_all][sylva.handler.Handler.search_all] are used
to execute the search and can be interchanged depending on whether or not recursive searching is desired.

Further functionality is documented elsewhere throughout this reference material.

## Generic search

```python
from sylva.handler import Handler

handler = Handler()
handler.branch_all('username')
results = handler.collector.get_data() #(1)!

print(results)
```

1.  [Handler][sylva.handler.Handler]'s member collector is a [sylva.Collector][] object where method get_data() returns a [pandas.DataFrame][]{target="_blank"}

## Targeted search

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
