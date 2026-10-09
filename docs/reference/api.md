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

# API reference

## Geometry constructors

Import geometry models from `cql2json_pydantic`. The first argument accepts lists
or tuples; additional fields such as `bbox` are keyword arguments.

| Model | First argument | Coordinate structure |
| --- | --- | --- |
| `Point` | `coordinates` | One position |
| `Linestring` | `coordinates` | Positions along a line |
| `Polygon` | `coordinates` | Rings, exterior first, then holes |
| `Multipoint` | `coordinates` | Positions |
| `Multilinestring` | `coordinates` | Lines of positions |
| `Multipolygon` | `coordinates` | Polygons of rings of positions |
| `Geometrycollection` | `geometries` | At least two geometry model instances |

These are Pydantic models. They retain `model_validate()`,
`model_validate_json()`, `model_dump()`, and `model_dump_json()`.
Keyword construction and existing generated coordinate wrappers remain supported.
The CQL2 schema and its validation constraints are unchanged.

See [Build geometries](../how-to/build-geometries.md) for runnable examples.

## Package API

::: cql2json_pydantic

## Generated models

::: cql2json_pydantic.models
