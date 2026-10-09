# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

import cql2json_pydantic as cql


@pytest.mark.parametrize(
    ("geometry", "expected"),
    [
        (cql.Point((-115.81, 37.24)), {"type": "Point", "coordinates": [-115.81, 37.24]}),
        (cql.Linestring(((0, 0), (1, 1))), {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}),
        (
            cql.Polygon((((0, 0), (1, 0), (1, 1), (0, 0)),)),
            {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
        ),
        (cql.Multipoint(((0, 0), (1, 1))), {"type": "MultiPoint", "coordinates": [[0, 0], [1, 1]]}),
        (
            cql.Multilinestring((((0, 0), (1, 1)),)),
            {"type": "MultiLineString", "coordinates": [[[0, 0], [1, 1]]]},
        ),
        (
            cql.Multipolygon([[[(0, 0), (1, 0), (1, 1), (0, 0)]]]),
            {"type": "MultiPolygon", "coordinates": [[[[0, 0], [1, 0], [1, 1], [0, 0]]]]},
        ),
        (
            cql.Geometrycollection((cql.Point((0, 0)), cql.Point((1, 1)))),
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point", "coordinates": [0, 0]},
                    {"type": "Point", "coordinates": [1, 1]},
                ],
            },
        ),
    ],
)
def test_positional_geometries_preserve_serialization(
    geometry: BaseModel, expected: dict[str, object]
) -> None:
    assert geometry.model_dump(mode="json", exclude_none=True, warnings="error") == expected
    assert type(geometry).model_validate(expected) == geometry
    assert type(geometry).model_validate_json(geometry.model_dump_json()) == geometry
    assert type(geometry)(**expected) == geometry


def test_positional_geometry_serializes_in_spatial_filter() -> None:
    predicate = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_INTERSECTS,
        args=[cql.PropertyRef(property="geometry"), cql.Point((-115.81, 37.24))],
    )
    expected = {
        "op": "s_intersects",
        "args": [{"property": "geometry"}, {"type": "Point", "coordinates": [-115.81, 37.24]}],
    }
    assert predicate.model_dump(mode="json", exclude_none=True, warnings="error") == expected
    assert cql.SpatialPredicate.model_validate(expected) == predicate


def test_point_preserves_keywords_bbox_extra_members_and_precision() -> None:
    point = cql.Point((-115.123456789, 37.24, 100), bbox=[-116, 37, -115, 38], label="site")
    assert point == cql.Point(
        coordinates=[-115.123456789, 37.24, 100], bbox=[-116, 37, -115, 38], label="site"
    )
    assert point.model_dump(mode="json", exclude_none=True) == {
        "type": "Point",
        "coordinates": [-115.123456789, 37.24, 100],
        "bbox": [-116, 37, -115, 38],
        "label": "site",
    }


def test_linestring_accepts_raw_lists_and_existing_coordinate_models() -> None:
    line = cql.Linestring(([0, 0], cql.LinestringCoordinate([1, 1])))
    assert line == cql.Linestring(
        coordinates=[cql.LinestringCoordinate([0, 0]), cql.LinestringCoordinate([1, 1])]
    )


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (cql.Point, {"coordinates": [0]}),
        (cql.Point, {"coordinates": None}),
        (cql.Point, {"coordinates": [0, 0], "type": "Polygon"}),
        (cql.Point, {"coordinates": [0, 0], "bbox": [0, 0]}),
        (cql.Point, {}),
        (cql.Linestring, {"coordinates": [[0, 0]]}),
        (cql.Polygon, {"coordinates": [[[0, 0], [1, 1], [0, 0]]]}),
        (cql.Multipoint, {"coordinates": [[0]]}),
        (cql.Multilinestring, {"coordinates": [[[0, 0]]]}),
        (cql.Multipolygon, {"coordinates": [[[[0, 0]]]]}),
        (cql.Geometrycollection, {"geometries": [{"type": "Point", "coordinates": [0, 0]}]}),
    ],
)
def test_geometry_validation_preserves_constraints(
    model: type[BaseModel], payload: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_positional_construction_validates_coordinates() -> None:
    with pytest.raises(ValidationError):
        cql.Point((0,))
    with pytest.raises(ValidationError):
        cql.Linestring(((0, 0),))
    with pytest.raises(ValidationError):
        cql.Geometrycollection((cql.Point((0, 0)),))
