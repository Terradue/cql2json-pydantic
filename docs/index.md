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

# CQL2 JSON Pydantic

Pydantic v2 models for building CQL2 JSON filters.

Use these docs by intent:

- [Tutorials](tutorials/): learn by completing a guided path.
- [How-to guides](how-to/): solve specific tasks.
- [Reference](reference/): look up commands, APIs, and configuration.
- [Explanation](explanation/): understand design decisions and concepts.

## Quick start

```bash
pip install cql2json-pydantic
```

```python
from cql2json_pydantic import BinaryComparisonPredicate, BinaryComparisonPredicateOp, PropertyRef

query = BinaryComparisonPredicate(
    op=BinaryComparisonPredicateOp.EQUAL,
    args=[PropertyRef(property="city"), "Toronto"],
)
print(query.model_dump_json(exclude_none=True))
```

Output:

```json
{"op":"=","args":[{"property":"city"},"Toronto"]}
```

Use `model_dump_json(indent=2, exclude_none=True)` for formatted JSON, or
`model_dump(mode="json", exclude_none=True)` for a JSON-compatible Python dictionary.

See [more filter examples and their JSON output](how-to/build-filter.md).

For spatial filters, construct a geometry directly from coordinates:

```python
import cql2json_pydantic as cql

point = cql.Point((-115.81, 37.24))
print(point.model_dump_json(exclude_none=True))
```

```json
{"type":"Point","coordinates":[-115.81,37.24]}
```

See [Build geometries](how-to/build-geometries.md) for all seven geometry types,
coordinate nesting, and validation.
