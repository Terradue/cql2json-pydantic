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

# Build geometries

Pass coordinates directly to the geometry constructor as lists or tuples.
Positions use longitude, latitude order. Each model supplies its GeoJSON `type`
automatically and validates its input using the existing CQL2 model constraints.

## Construct a point

```python
import cql2json_pydantic as cql

point = cql.Point((-115.81, 37.24))
print(point.model_dump_json(exclude_none=True))
```

Output:

```json
{"type":"Point","coordinates":[-115.81,37.24]}
```

## Construct lines, polygons, and multi-geometries

Use nested sequences for more complex shapes. A polygon contains an exterior ring
followed by any interior rings (holes). Each multi-geometry adds a sequence around
its component coordinates.

```python
import cql2json_pydantic as cql

line = cql.Linestring([(0, 0), (1, 1)])
polygon = cql.Polygon([
    [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)],
    [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)],
])
points = cql.Multipoint([(0, 0), (1, 1)])
lines = cql.Multilinestring([
    [(0, 0), (1, 1)],
    [(2, 2), (3, 3)],
])
polygons = cql.Multipolygon([
    [[(0, 0), (1, 0), (1, 1), (0, 0)]],
    [[(2, 2), (3, 2), (3, 3), (2, 2)]],
])
```

No coordinate wrapper objects are needed for these inputs. The resulting objects
remain Pydantic models; their stored coordinate fields retain the generated types.

## Group geometries

Pass model instances to `Geometrycollection`. The CQL2 schema requires at least
two members, each a point, line, polygon, or multi-geometry; nested geometry
collections are not accepted.

```python
import cql2json_pydantic as cql

collection = cql.Geometrycollection([
    cql.Point((0, 0)),
    cql.Linestring([(0, 0), (1, 1)]),
])
```

Use any of these geometry models as an operand in a spatial predicate, as shown
in [Intersect a point](build-filter.md#intersect-a-point).

## Supply optional fields or use keyword construction

Optional fields remain keyword arguments. Existing keyword-only calls and
coordinate wrappers continue to work:

```python
import cql2json_pydantic as cql

point = cql.Point((0, 0), bbox=[-1, -1, 1, 1])
same_point = cql.Point(coordinates=[0, 0], bbox=[-1, -1, 1, 1])
assert point == same_point

line = cql.Linestring(coordinates=[
    cql.LinestringCoordinate(root=[0, 0]),
    cql.LinestringCoordinate(root=[1, 1]),
])
assert line == cql.Linestring([(0, 0), (1, 1)])
```

`BboxLiteral` continues to use a keyword argument:
`cql.BboxLiteral(bbox=[-1, -1, 1, 1])`.

## Validate and serialize

Invalid input raises `pydantic.ValidationError` during construction. For example,
a position needs at least two numbers, a line needs at least two positions, and a
polygon ring needs at least four positions. Validation enforces the existing
schema constraints; it does not perform geometric topology checks.

```python
import cql2json_pydantic as cql
from pydantic import ValidationError

try:
    cql.Point((0,))
except ValidationError:
    print("A point needs at least two coordinates.")
```

Use `model_dump_json(exclude_none=True)` for JSON text, or
`model_dump(mode="json", exclude_none=True)` for a JSON-compatible dictionary.
`exclude_none=True` omits an unset `bbox`. Avoid `exclude_defaults=True` or
`exclude_unset=True` when producing GeoJSON: these may omit the automatically
supplied `type` field.

Read serialized geometry back using the corresponding model:

```python
import cql2json_pydantic as cql

point = cql.Point((-115.81, 37.24))
payload = point.model_dump(mode="json", exclude_none=True)
restored = cql.Point.model_validate(payload)
assert restored == point
assert cql.Point.model_validate_json(point.model_dump_json(exclude_none=True)) == point
```
