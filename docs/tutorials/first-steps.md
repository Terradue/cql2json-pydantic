<!--
Copyright 2026 Terradue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# First steps

In this tutorial, you will install `cql2json-pydantic` and build a CQL2 JSON filter.

## Install

```bash
pip install cql2json-pydantic
```

## Build a filter

```python
from cql2json_pydantic import BinaryComparisonPredicate, BinaryComparisonPredicateOp, PropertyRef

query = BinaryComparisonPredicate(
    op=BinaryComparisonPredicateOp.EQUAL,
    args=[PropertyRef(property="city"), "Toronto"],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "=",
  "args": [
    {
      "property": "city"
    },
    "Toronto"
  ]
}
```

`model_dump_json()` returns a JSON string. Set `indent=2` to make it readable;
omit `indent` for compact output. To obtain a Python dictionary for an API client,
use `query.model_dump(mode="json", exclude_none=True)`.

## Next step

Explore [more filter examples and their JSON output](../how-to/build-filter.md),
including logical combinations, list membership, spatial predicates, time intervals,
and arithmetic expressions.

For spatial filters, follow [Build geometries](../how-to/build-geometries.md)
to construct points, lines, and polygons directly from coordinate lists or tuples.
