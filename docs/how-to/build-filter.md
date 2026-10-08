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

# Build and render filters

The examples below are independent: copy any Python block to construct a filter
and print the JSON shown immediately after it. Import models from
`cql2json_pydantic`; the shorter `cql` alias keeps nested expressions readable.

The models construct and serialize CQL2 JSON expressions. A service that supports
the operators and properties in your filter evaluates them.

## Choose a serialization method

- `query.model_dump_json(exclude_none=True)` returns a compact JSON **string**.
- `query.model_dump_json(indent=2, exclude_none=True)` returns a formatted JSON
  **string**, as shown below.
- `query.model_dump(mode="json", exclude_none=True)` returns a Python **dictionary**
  containing JSON-compatible values, suitable for an HTTP client's `json=` parameter.

Use `mode="json"` when producing a dictionary so enums and tuples are converted to
JSON-compatible values. Use `exclude_none=True` to omit unset optional fields,
such as a geometry's `bbox`. Avoid `exclude_defaults=True` or `exclude_unset=True`
for these examples: they can omit required `op` or geometry `type` values that the
models supply by default.

JSON number formatting can differ from the constructor input: for example, the
numeric operand `20` may serialize as `20.0`. Both represent the same JSON number.

## Compare a property with a value

Select features whose `city` property equals `Toronto`. A `PropertyRef` identifies a feature property; a plain string is a literal value.

```python
import cql2json_pydantic as cql

query = cql.BinaryComparisonPredicate(
    op=cql.BinaryComparisonPredicateOp.EQUAL,
    args=[cql.PropertyRef(property="city"), "Toronto"],
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

## Combine filters with AND, OR, and NOT

Select features in Toronto or Ottawa with cloud cover below 20, excluding features whose geometry is null. Each nested expression is another model instance.

```python
import cql2json_pydantic as cql

query = cql.AndOrExpression(
    op=cql.AndOrExpressionOp.AND,
    args=[
        cql.AndOrExpression(
            op=cql.AndOrExpressionOp.OR,
            args=[
                cql.BinaryComparisonPredicate(
                    op=cql.BinaryComparisonPredicateOp.EQUAL,
                    args=[cql.PropertyRef(property="city"), "Toronto"],
                ),
                cql.BinaryComparisonPredicate(
                    op=cql.BinaryComparisonPredicateOp.EQUAL,
                    args=[cql.PropertyRef(property="city"), "Ottawa"],
                ),
            ],
        ),
        cql.BinaryComparisonPredicate(
            op=cql.BinaryComparisonPredicateOp.LESS_THAN,
            args=[cql.PropertyRef(property="cloud_cover"), 20],
        ),
        cql.NotExpression(
            args=[cql.IsNullPredicate(args=[cql.PropertyRef(property="geometry")])],
        ),
    ],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "and",
  "args": [
    {
      "op": "or",
      "args": [
        {
          "op": "=",
          "args": [
            {
              "property": "city"
            },
            "Toronto"
          ]
        },
        {
          "op": "=",
          "args": [
            {
              "property": "city"
            },
            "Ottawa"
          ]
        }
      ]
    },
    {
      "op": "<",
      "args": [
        {
          "property": "cloud_cover"
        },
        20.0
      ]
    },
    {
      "op": "not",
      "args": [
        {
          "op": "isNull",
          "args": [
            {
              "property": "geometry"
            }
          ]
        }
      ]
    }
  ]
}
```

## Match a value from a list

Select features whose `city` is one of three names. The `in` operands are a tuple: first the value to compare, then the list of allowed values. The tuple serializes as a JSON array.

```python
import cql2json_pydantic as cql

query = cql.IsInListPredicate(
    args=(cql.PropertyRef(property="city"), ["Toronto", "Ottawa", "Montreal"]),
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "in",
  "args": [
    {
      "property": "city"
    },
    [
      "Toronto",
      "Ottawa",
      "Montreal"
    ]
  ]
}
```

## Match a text pattern

Match names against `Smith%`. The fixed `like` operator is supplied by the model, so it does not need an explicit `op` argument.

```python
import cql2json_pydantic as cql

query = cql.IsLikePredicate(
    args=(cql.PropertyRef(property="name"), "Smith%"),
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "like",
  "args": [
    {
      "property": "name"
    },
    "Smith%"
  ]
}
```

## Intersect a point

Select geometries that intersect a GeoJSON point. Coordinates are supplied in longitude, latitude order. `Point` supplies its `type` value automatically; `exclude_none=True` omits its unset optional `bbox`.

```python
import cql2json_pydantic as cql

query = cql.SpatialPredicate(
    op=cql.SpatialPredicateOp.S_INTERSECTS,
    args=[
        cql.PropertyRef(property="geometry"),
        cql.Point(coordinates=[-79.38, 43.65]),
    ],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "s_intersects",
  "args": [
    {
      "property": "geometry"
    },
    {
      "type": "Point",
      "coordinates": [
        -79.38,
        43.65
      ]
    }
  ]
}
```

## Filter within a bounding box

Select geometries within a bounding box, using `[west, south, east, north]` coordinates.

```python
import cql2json_pydantic as cql

query = cql.SpatialPredicate(
    op=cql.SpatialPredicateOp.S_WITHIN,
    args=[
        cql.PropertyRef(property="geometry"),
        cql.BboxLiteral(bbox=[-80.0, 43.0, -79.0, 44.0]),
    ],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "s_within",
  "args": [
    {
      "property": "geometry"
    },
    {
      "bbox": [
        -80.0,
        43.0,
        -79.0,
        44.0
      ]
    }
  ]
}
```

## Filter by a time interval

Select observations during a bounded interval. `TimestampString` wraps each UTC timestamp and serializes directly to a string inside the interval array.

```python
import cql2json_pydantic as cql

query = cql.TemporalPredicate(
    op=cql.TemporalPredicateOp.T_DURING,
    args=[
        cql.PropertyRef(property="observed_at"),
        cql.IntervalInstance(
            interval=[
                cql.TimestampString(root="2025-01-01T00:00:00Z"),
                cql.TimestampString(root="2025-02-01T00:00:00Z"),
            ],
        ),
    ],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "t_during",
  "args": [
    {
      "property": "observed_at"
    },
    {
      "interval": [
        "2025-01-01T00:00:00Z",
        "2025-02-01T00:00:00Z"
      ]
    }
  ]
}
```

## Use an open interval

Use the literal `".."` for an unbounded endpoint. This example selects events whose time intersects an interval with no start bound.

```python
import cql2json_pydantic as cql

query = cql.TemporalPredicate(
    op=cql.TemporalPredicateOp.T_INTERSECTS,
    args=[
        cql.PropertyRef(property="event_time"),
        cql.IntervalInstance(
            interval=["..", cql.TimestampString(root="2025-02-01T00:00:00Z")],
        ),
    ],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": "t_intersects",
  "args": [
    {
      "property": "event_time"
    },
    {
      "interval": [
        "..",
        "2025-02-01T00:00:00Z"
      ]
    }
  ]
}
```

## Nest arithmetic expressions and functions

Compare a property with the result of adding 10 to a function call. `FunctionRef` represents a function supported by the receiving service; the models build the expression without evaluating it.

```python
import cql2json_pydantic as cql

query = cql.BinaryComparisonPredicate(
    op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
    args=[
        cql.PropertyRef(property="height"),
        cql.ArithmeticExpression(
            op=cql.ArithmeticExpressionOp.ADD,
            args=[
                cql.FunctionRef(
                    op="average",
                    args=[cql.PropertyRef(property="nearby_heights")],
                ),
                10,
            ],
        ),
    ],
)
print(query.model_dump_json(indent=2, exclude_none=True))
```

Output:

```json
{
  "op": ">",
  "args": [
    {
      "property": "height"
    },
    {
      "op": "+",
      "args": [
        {
          "op": "average",
          "args": [
            {
              "property": "nearby_heights"
            }
          ]
        },
        10.0
      ]
    }
  ]
}
```

## Send a JSON-compatible dictionary

Use the dictionary form when another library handles JSON encoding for you:

```python
import json

import cql2json_pydantic as cql

query = cql.BinaryComparisonPredicate(
    op=cql.BinaryComparisonPredicateOp.EQUAL,
    args=[cql.PropertyRef(property="city"), "Toronto"],
)
payload = query.model_dump(mode="json", exclude_none=True)
print(json.dumps(payload, indent=2))
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

For an HTTP client with a `json=` parameter, pass `payload` to that parameter.
Passing the result of `model_dump_json()` to `json=` would encode the JSON string
again instead of sending a filter object. The receiving API determines where the
filter belongs in its request.

## Read a filter back into a model

When you know the filter's model type, validate a JSON string with
`model_validate_json()`:

```python
import cql2json_pydantic as cql

encoded = '{"op":"=","args":[{"property":"city"},"Toronto"]}'
query = cql.BinaryComparisonPredicate.model_validate_json(encoded)
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

Use `model_validate(payload)` for an existing dictionary. Validation uses the
selected model's field definitions and raises `pydantic.ValidationError` for
inputs that do not satisfy them.
