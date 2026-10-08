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

"""Construct the OGC CQL2 1.0 examples using the public model API.

Fixtures are unmodified upstream JSON. Each test constructs its filter independently
so nested models cannot silently fall back to permissive function references.
JSON numbers compare by value (4 and 4.0 are equivalent); booleans remain distinct.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, JsonValue, TypeAdapter

import cql2json_pydantic as cql


def test_every_fixture_has_a_construction_test() -> None:
    fixtures = Path(__file__).parent / "fixtures" / "ogc_cql2_json"
    fixture_names = {path.stem for path in fixtures.glob("*.json")}
    test_names = {
        name.removeprefix("test_build_") for name in globals() if name.startswith("test_build_")
    }
    assert fixture_names
    assert fixture_names == test_names


def _assert_json_equal(actual: JsonValue, expected: JsonValue) -> None:
    """Compare JSON structures without treating booleans as numbers."""
    assert isinstance(actual, bool) == isinstance(expected, bool)
    assert actual == expected
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        for key, value in expected.items():
            _assert_json_equal(actual[key], value)
    elif isinstance(expected, list):
        assert isinstance(actual, list)
        for actual_item, expected_item in zip(actual, expected, strict=True):
            _assert_json_equal(actual_item, expected_item)


def _assert_example(filename: str, expression: BaseModel) -> None:
    """Match both serialization paths and validation against an upstream example."""
    fixture = Path(__file__).parent / "fixtures" / "ogc_cql2_json" / filename
    adapter = TypeAdapter(JsonValue)
    expected = adapter.validate_json(fixture.read_bytes())
    actual = expression.model_dump_json(exclude_none=True, warnings="error")
    _assert_json_equal(adapter.validate_json(actual), expected)
    _assert_json_equal(
        adapter.validate_python(
            expression.model_dump(mode="json", exclude_none=True, warnings="error")
        ),
        expected,
    )
    restored = type(expression).model_validate_json(fixture.read_bytes())
    _assert_json_equal(
        adapter.validate_json(restored.model_dump_json(exclude_none=True, warnings="error")),
        expected,
    )


def test_build_clause6_01() -> None:
    expression = cql.FunctionRef(op="avg", args=[cql.PropertyRef(property="windSpeed")])
    _assert_example("clause6_01.json", expression)


def test_build_clause6_02a() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL, args=[cql.PropertyRef(property="city"), "Toronto"]
    )
    _assert_example("clause6_02a.json", expression)


def test_build_clause6_02b() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.LESS_THAN,
        args=[cql.FunctionRef(op="avg", args=[cql.PropertyRef(property="windSpeed")]), 4],
    )
    _assert_example("clause6_02b.json", expression)


def test_build_clause6_02c() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
        args=[
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.SUBTRACT,
                args=[cql.PropertyRef(property="balance"), 150.0],
            ),
            0,
        ],
    )
    _assert_example("clause6_02c.json", expression)


def test_build_clause6_02d() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN_OR_EQUAL,
        args=[cql.PropertyRef(property="updated"), cql.DateInstant(date="1970-01-01")],
    )
    _assert_example("clause6_02d.json", expression)


def test_build_clause6_03() -> None:
    expression = cql.NotExpression(
        args=[cql.IsNullPredicate(args=[cql.PropertyRef(property="geometry")])]
    )
    _assert_example("clause6_03.json", expression)


def test_build_clause7_01() -> None:
    expression = cql.IsLikePredicate(args=(cql.PropertyRef(property="name"), "Smith%"))
    _assert_example("clause7_01.json", expression)


def test_build_clause7_02() -> None:
    expression = cql.IsBetweenPredicate(args=[cql.PropertyRef(property="depth"), 100.0, 150.0])
    _assert_example("clause7_02.json", expression)


def test_build_clause7_03a() -> None:
    expression = cql.IsInListPredicate(
        args=(cql.PropertyRef(property="cityName"), ["Toronto", "Frankfurt", "Tokyo", "New York"])
    )
    _assert_example("clause7_03a.json", expression)


def test_build_clause7_03b() -> None:
    expression = cql.NotExpression(
        args=[cql.IsInListPredicate(args=(cql.PropertyRef(property="category"), [1, 2, 3, 4]))]
    )
    _assert_example("clause7_03b.json", expression)


def test_build_clause7_04() -> None:
    expression = cql.IsInListPredicate(
        args=(
            cql.Casei(args=[cql.PropertyRef(property="road_class")]),
            [cql.Casei(args=["Οδος"]), cql.Casei(args=["Straße"])],
        )
    )
    _assert_example("clause7_04.json", expression)


def test_build_clause7_05() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            cql.Accenti(args=[cql.PropertyRef(property="etat_vol")]),
            cql.Accenti(args=["débárquér"]),
        ],
    )
    _assert_example("clause7_05.json", expression)


def test_build_clause7_07() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_INTERSECTS,
        args=[cql.PropertyRef(property="geometry"), cql.Point(coordinates=[36.319836, 32.288087])],
    )
    _assert_example("clause7_07.json", expression)


def test_build_clause7_10() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_CROSSES,
        args=[
            cql.PropertyRef(property="road"),
            cql.Polygon(
                coordinates=[
                    cql.Coordinate1(
                        root=[
                            cql.Coordinate1Item(root=[43.7286, -79.2986]),
                            cql.Coordinate1Item(root=[43.7311, -79.2996]),
                            cql.Coordinate1Item(root=[43.7323, -79.2972]),
                            cql.Coordinate1Item(root=[43.7326, -79.2971]),
                            cql.Coordinate1Item(root=[43.735, -79.2981]),
                            cql.Coordinate1Item(root=[43.735, -79.2982]),
                            cql.Coordinate1Item(root=[43.7352, -79.2982]),
                            cql.Coordinate1Item(root=[43.7357, -79.2956]),
                            cql.Coordinate1Item(root=[43.7337, -79.2948]),
                            cql.Coordinate1Item(root=[43.7343, -79.2933]),
                            cql.Coordinate1Item(root=[43.7339, -79.2923]),
                            cql.Coordinate1Item(root=[43.7327, -79.2947]),
                            cql.Coordinate1Item(root=[43.732, -79.2942]),
                            cql.Coordinate1Item(root=[43.7322, -79.2937]),
                            cql.Coordinate1Item(root=[43.7306, -79.293]),
                            cql.Coordinate1Item(root=[43.7303, -79.293]),
                            cql.Coordinate1Item(root=[43.7299, -79.2928]),
                            cql.Coordinate1Item(root=[43.7286, -79.2986]),
                        ]
                    )
                ]
            ),
        ],
    )
    _assert_example("clause7_10.json", expression)


def test_build_clause7_12() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_INTERSECTS,
        args=[
            cql.PropertyRef(property="event_time"),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1969-07-16T05:32:00Z"),
                    cql.TimestampString(root="1969-07-24T16:50:35Z"),
                ]
            ),
        ],
    )
    _assert_example("clause7_12.json", expression)


def test_build_clause7_13() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_DURING,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="touchdown"),
                    cql.PropertyRef(property="liftOff"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1969-07-16T13:32:00Z"),
                    cql.TimestampString(root="1969-07-24T16:50:35Z"),
                ]
            ),
        ],
    )
    _assert_example("clause7_13.json", expression)


def test_build_clause7_15() -> None:
    expression = cql.ArrayPredicate(
        op=cql.ArrayPredicateOp.A_CONTAINS,
        args=[cql.PropertyRef(property="layer:ids"), ["layers-ca", "layers-us"]],
    )
    _assert_example("clause7_15.json", expression)


def test_build_clause7_16() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_CROSSES,
        args=[
            cql.Linestring(
                coordinates=[
                    cql.Coordinate(root=[43.72992, -79.2998]),
                    cql.Coordinate(root=[43.73005, -79.2991]),
                    cql.Coordinate(root=[43.73006, -79.2984]),
                    cql.Coordinate(root=[43.7314, -79.2956]),
                    cql.Coordinate(root=[43.73259, -79.295]),
                    cql.Coordinate(root=[43.73266, -79.2945]),
                    cql.Coordinate(root=[43.7332, -79.2936]),
                    cql.Coordinate(root=[43.73378, -79.2936]),
                    cql.Coordinate(root=[43.73486, -79.2917]),
                ]
            ),
            cql.Polygon(
                coordinates=[
                    cql.Coordinate1(
                        root=[
                            cql.Coordinate1Item(root=[43.7286, -79.2986]),
                            cql.Coordinate1Item(root=[43.7311, -79.2996]),
                            cql.Coordinate1Item(root=[43.7323, -79.2972]),
                            cql.Coordinate1Item(root=[43.7326, -79.2971]),
                            cql.Coordinate1Item(root=[43.735, -79.2981]),
                            cql.Coordinate1Item(root=[43.735, -79.2982]),
                            cql.Coordinate1Item(root=[43.7352, -79.2982]),
                            cql.Coordinate1Item(root=[43.7357, -79.2956]),
                            cql.Coordinate1Item(root=[43.7337, -79.2948]),
                            cql.Coordinate1Item(root=[43.7343, -79.2933]),
                            cql.Coordinate1Item(root=[43.7339, -79.2923]),
                            cql.Coordinate1Item(root=[43.7327, -79.2947]),
                            cql.Coordinate1Item(root=[43.732, -79.2942]),
                            cql.Coordinate1Item(root=[43.7322, -79.2937]),
                            cql.Coordinate1Item(root=[43.7306, -79.293]),
                            cql.Coordinate1Item(root=[43.7303, -79.293]),
                            cql.Coordinate1Item(root=[43.7299, -79.2928]),
                            cql.Coordinate1Item(root=[43.7286, -79.2986]),
                        ]
                    )
                ]
            ),
        ],
    )
    _assert_example("clause7_16.json", expression)


def test_build_clause7_17() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_DURING,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1969-07-20T20:17:40Z"),
                    cql.TimestampString(root="1969-07-21T17:54:00Z"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1969-07-16T13:32:00Z"),
                    cql.TimestampString(root="1969-07-24T16:50:35Z"),
                ]
            ),
        ],
    )
    _assert_example("clause7_17.json", expression)


def test_build_clause7_18() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_WITHIN,
        args=[
            cql.PropertyRef(property="road"),
            cql.FunctionRef(op="Buffer", args=[cql.PropertyRef(property="geometry"), 10, "m"]),
        ],
    )
    _assert_example("clause7_18.json", expression)


def test_build_clause7_19() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
        args=[
            cql.PropertyRef(property="vehicle_height"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.SUBTRACT,
                args=[cql.PropertyRef(property="bridge_clearance"), 1],
            ),
        ],
    )
    _assert_example("clause7_19.json", expression)


def test_build_example01() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[cql.PropertyRef(property="landsat:scene_id"), "LC82030282019133LGN00"],
    )
    _assert_example("example01.json", expression)


def test_build_example02() -> None:
    expression = cql.IsLikePredicate(args=(cql.PropertyRef(property="eo:instrument"), "OLI%"))
    _assert_example("example02.json", expression)


def test_build_example03() -> None:
    expression = cql.IsInListPredicate(
        args=(cql.PropertyRef(property="landsat:wrs_path"), ["153", "154", "15X"])
    )
    _assert_example("example03.json", expression)


def test_build_example04() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.LESS_THAN,
                args=[cql.PropertyRef(property="eo:cloud_cover"), 0.1],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="landsat:wrs_row"), 28],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="landsat:wrs_path"), 203],
            ),
        ],
    )
    _assert_example("example04.json", expression)


def test_build_example05a() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.OR,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="eo:cloud_cover"), 0.1],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="eo:cloud_cover"), 0.2],
            ),
        ],
    )
    _assert_example("example05a.json", expression)


def test_build_example05b() -> None:
    expression = cql.IsInListPredicate(
        args=(cql.PropertyRef(property="eo:cloud_cover"), [0.1, 0.2])
    )
    _assert_example("example05b.json", expression)


def test_build_example06a() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.IsBetweenPredicate(args=[cql.PropertyRef(property="eo:cloud_cover"), 0.1, 0.2]),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="landsat:wrs_row"), 28],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="landsat:wrs_path"), 203],
            ),
        ],
    )
    _assert_example("example06a.json", expression)


def test_build_example06b() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.GREATER_THAN_OR_EQUAL,
                args=[cql.PropertyRef(property="eo:cloud_cover"), 0.1],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.LESS_THAN_OR_EQUAL,
                args=[cql.PropertyRef(property="eo:cloud_cover"), 0.2],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="landsat:wrs_row"), 28],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="landsat:wrs_path"), 203],
            ),
        ],
    )
    _assert_example("example06b.json", expression)


def test_build_example07() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.IsLikePredicate(args=(cql.PropertyRef(property="eo:instrument"), "OLI%")),
            cql.SpatialPredicate(
                op=cql.SpatialPredicateOp.S_INTERSECTS,
                args=[
                    cql.PropertyRef(property="footprint"),
                    cql.Polygon(
                        coordinates=[
                            cql.Coordinate1(
                                root=[
                                    cql.Coordinate1Item(root=[43.5845, -79.5442]),
                                    cql.Coordinate1Item(root=[43.6079, -79.4893]),
                                    cql.Coordinate1Item(root=[43.5677, -79.4632]),
                                    cql.Coordinate1Item(root=[43.6129, -79.3925]),
                                    cql.Coordinate1Item(root=[43.6223, -79.3238]),
                                    cql.Coordinate1Item(root=[43.6576, -79.3163]),
                                    cql.Coordinate1Item(root=[43.7945, -79.1178]),
                                    cql.Coordinate1Item(root=[43.8144, -79.1542]),
                                    cql.Coordinate1Item(root=[43.8555, -79.1714]),
                                    cql.Coordinate1Item(root=[43.7509, -79.639]),
                                    cql.Coordinate1Item(root=[43.5845, -79.5442]),
                                ]
                            )
                        ]
                    ),
                ],
            ),
        ],
    )
    _assert_example("example07.json", expression)


def test_build_example08() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="beamMode"), "ScanSAR Narrow"],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="swathDirection"), "ascending"],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="polarization"), "HH+VV+HV+VH"],
            ),
            cql.SpatialPredicate(
                op=cql.SpatialPredicateOp.S_INTERSECTS,
                args=[
                    cql.PropertyRef(property="footprint"),
                    cql.Polygon(
                        coordinates=[
                            cql.Coordinate1(
                                root=[
                                    cql.Coordinate1Item(root=[-77.117938, 38.93686]),
                                    cql.Coordinate1Item(root=[-77.040604, 39.995648]),
                                    cql.Coordinate1Item(root=[-76.910536, 38.892912]),
                                    cql.Coordinate1Item(root=[-77.039359, 38.791753]),
                                    cql.Coordinate1Item(root=[-77.047906, 38.841462]),
                                    cql.Coordinate1Item(root=[-77.034183, 38.840655]),
                                    cql.Coordinate1Item(root=[-77.033142, 38.85749]),
                                    cql.Coordinate1Item(root=[-77.117938, 38.93686]),
                                ]
                            )
                        ]
                    ),
                ],
            ),
        ],
    )
    _assert_example("example08.json", expression)


def test_build_example09() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
        args=[cql.PropertyRef(property="floors"), 5],
    )
    _assert_example("example09.json", expression)


def test_build_example10() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.LESS_THAN_OR_EQUAL,
        args=[cql.PropertyRef(property="taxes"), 500],
    )
    _assert_example("example10.json", expression)


def test_build_example11() -> None:
    expression = cql.IsLikePredicate(args=(cql.PropertyRef(property="owner"), "%Jones%"))
    _assert_example("example11.json", expression)


def test_build_example12() -> None:
    expression = cql.IsLikePredicate(args=(cql.PropertyRef(property="owner"), "Mike%"))
    _assert_example("example12.json", expression)


def test_build_example13() -> None:
    expression = cql.NotExpression(
        args=[cql.IsLikePredicate(args=(cql.PropertyRef(property="owner"), "%Mike%"))]
    )
    _assert_example("example13.json", expression)


def test_build_example14() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[cql.PropertyRef(property="swimming_pool"), True],
    )
    _assert_example("example14.json", expression)


def test_build_example15() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
                args=[cql.PropertyRef(property="floors"), 5],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="swimming_pool"), True],
            ),
        ],
    )
    _assert_example("example15.json", expression)


def test_build_example16() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="swimming_pool"), True],
            ),
            cql.AndOrExpression(
                op=cql.AndOrExpressionOp.OR,
                args=[
                    cql.BinaryComparisonPredicate(
                        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
                        args=[cql.PropertyRef(property="floors"), 5],
                    ),
                    cql.IsLikePredicate(args=(cql.PropertyRef(property="material"), "brick%")),
                    cql.IsLikePredicate(args=(cql.PropertyRef(property="material"), "%brick")),
                ],
            ),
        ],
    )
    _assert_example("example16.json", expression)


def test_build_example17() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.OR,
        args=[
            cql.AndOrExpression(
                op=cql.AndOrExpressionOp.AND,
                args=[
                    cql.BinaryComparisonPredicate(
                        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
                        args=[cql.PropertyRef(property="floors"), 5],
                    ),
                    cql.BinaryComparisonPredicate(
                        op=cql.BinaryComparisonPredicateOp.EQUAL,
                        args=[cql.PropertyRef(property="material"), "brick"],
                    ),
                ],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="swimming_pool"), True],
            ),
        ],
    )
    _assert_example("example17.json", expression)


def test_build_example18() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.OR,
        args=[
            cql.NotExpression(
                args=[
                    cql.BinaryComparisonPredicate(
                        op=cql.BinaryComparisonPredicateOp.LESS_THAN,
                        args=[cql.PropertyRef(property="floors"), 5],
                    )
                ]
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.EQUAL,
                args=[cql.PropertyRef(property="swimming_pool"), True],
            ),
        ],
    )
    _assert_example("example18.json", expression)


def test_build_example19() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.AndOrExpression(
                op=cql.AndOrExpressionOp.OR,
                args=[
                    cql.IsLikePredicate(args=(cql.PropertyRef(property="owner"), "mike%")),
                    cql.IsLikePredicate(args=(cql.PropertyRef(property="owner"), "Mike%")),
                ],
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.LESS_THAN,
                args=[cql.PropertyRef(property="floors"), 4],
            ),
        ],
    )
    _assert_example("example19.json", expression)


def test_build_example20() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_BEFORE,
        args=[cql.PropertyRef(property="built"), cql.DateInstant(date="2015-01-01")],
    )
    _assert_example("example20.json", expression)


def test_build_example21() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_AFTER,
        args=[cql.PropertyRef(property="built"), cql.DateInstant(date="2012-06-05")],
    )
    _assert_example("example21.json", expression)


def test_build_example22() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_DURING,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="2017-06-10T07:30:00Z"),
                    cql.TimestampString(root="2017-06-11T10:30:00Z"),
                ]
            ),
        ],
    )
    _assert_example("example22.json", expression)


def test_build_example23() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_WITHIN,
        args=[cql.PropertyRef(property="location"), cql.BboxLiteral(bbox=[-118, 33.8, -117.9, 34])],
    )
    _assert_example("example23.json", expression)


def test_build_example24() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_INTERSECTS,
        args=[
            cql.PropertyRef(property="geometry"),
            cql.Polygon(
                coordinates=[
                    cql.Coordinate1(
                        root=[
                            cql.Coordinate1Item(root=[-10, -10]),
                            cql.Coordinate1Item(root=[10, -10]),
                            cql.Coordinate1Item(root=[10, 10]),
                            cql.Coordinate1Item(root=[-10, -10]),
                        ]
                    )
                ]
            ),
        ],
    )
    _assert_example("example24.json", expression)


def test_build_example25() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
                args=[cql.PropertyRef(property="floors"), 5],
            ),
            cql.SpatialPredicate(
                op=cql.SpatialPredicateOp.S_WITHIN,
                args=[
                    cql.PropertyRef(property="geometry"),
                    cql.BboxLiteral(bbox=[-118, 33.8, -117.9, 34]),
                ],
            ),
        ],
    )
    _assert_example("example25.json", expression)


def test_build_example26() -> None:
    expression = cql.IsInListPredicate(
        args=(
            cql.Casei(args=[cql.PropertyRef(property="road_class")]),
            [cql.Casei(args=["Οδος"]), cql.Casei(args=["Straße"])],
        )
    )
    _assert_example("example26.json", expression)


def test_build_example27() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            cql.Accenti(args=[cql.PropertyRef(property="etat_vol")]),
            cql.Accenti(args=["débárquér"]),
        ],
    )
    _assert_example("example27.json", expression)


def test_build_example28() -> None:
    expression = cql.IsLikePredicate(
        args=(
            cql.Casei(args=[cql.PropertyRef(property="geophys:SURVEY_NAME")]),
            cql.PatternExpression1(args=["%calcutta%"]),
        )
    )
    _assert_example("example28.json", expression)


def test_build_example29() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[cql.PropertyRef(property="id"), "fa7e1920-9107-422d-a3db-c468cbc5d6df"],
    )
    _assert_example("example29.json", expression)


def test_build_example30() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.NOT_EQUAL,
        args=[cql.PropertyRef(property="id"), "fa7e1920-9107-422d-a3db-c468cbc5d6df"],
    )
    _assert_example("example30.json", expression)


def test_build_example31() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.LESS_THAN, args=[cql.PropertyRef(property="value"), 10]
    )
    _assert_example("example31.json", expression)


def test_build_example32() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
        args=[cql.PropertyRef(property="value"), 10],
    )
    _assert_example("example32.json", expression)


def test_build_example33() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.LESS_THAN_OR_EQUAL,
        args=[cql.PropertyRef(property="value"), 10],
    )
    _assert_example("example33.json", expression)


def test_build_example34() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN_OR_EQUAL,
        args=[cql.PropertyRef(property="value"), 10],
    )
    _assert_example("example34.json", expression)


def test_build_example35() -> None:
    expression = cql.IsLikePredicate(args=(cql.PropertyRef(property="name"), "foo%"))
    _assert_example("example35.json", expression)


def test_build_example36() -> None:
    expression = cql.NotExpression(
        args=[cql.IsLikePredicate(args=(cql.PropertyRef(property="name"), "foo%"))]
    )
    _assert_example("example36.json", expression)


def test_build_example37() -> None:
    expression = cql.IsBetweenPredicate(args=[cql.PropertyRef(property="value"), 10, 20])
    _assert_example("example37.json", expression)


def test_build_example38() -> None:
    expression = cql.NotExpression(
        args=[cql.IsBetweenPredicate(args=[cql.PropertyRef(property="value"), 10, 20])]
    )
    _assert_example("example38.json", expression)


def test_build_example39() -> None:
    expression = cql.IsInListPredicate(args=(cql.PropertyRef(property="value"), [1.0, 2.0, 3.0]))
    _assert_example("example39.json", expression)


def test_build_example40() -> None:
    expression = cql.NotExpression(
        args=[cql.IsInListPredicate(args=(cql.PropertyRef(property="value"), ["a", "b", "c"]))]
    )
    _assert_example("example40.json", expression)


def test_build_example41() -> None:
    expression = cql.IsNullPredicate(args=[cql.PropertyRef(property="value")])
    _assert_example("example41.json", expression)


def test_build_example42() -> None:
    expression = cql.NotExpression(
        args=[cql.IsNullPredicate(args=[cql.PropertyRef(property="value")])]
    )
    _assert_example("example42.json", expression)


def test_build_example43() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.AND,
        args=[
            cql.NotExpression(
                args=[cql.IsLikePredicate(args=(cql.PropertyRef(property="name"), "foo%"))]
            ),
            cql.BinaryComparisonPredicate(
                op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
                args=[cql.PropertyRef(property="value"), 10],
            ),
        ],
    )
    _assert_example("example43.json", expression)


def test_build_example44() -> None:
    expression = cql.AndOrExpression(
        op=cql.AndOrExpressionOp.OR,
        args=[
            cql.IsNullPredicate(args=[cql.PropertyRef(property="value")]),
            cql.IsBetweenPredicate(args=[cql.PropertyRef(property="value"), 10, 20]),
        ],
    )
    _assert_example("example44.json", expression)


def test_build_example45() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_INTERSECTS,
        args=[
            cql.PropertyRef(property="geometry"),
            cql.BboxLiteral(bbox=[-128.098193, -1.1, -99999.0, 180.0, 90.0, 100000.0]),
        ],
    )
    _assert_example("example45.json", expression)


def test_build_example46() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_EQUALS,
        args=[
            cql.Polygon(
                coordinates=[
                    cql.Coordinate1(
                        root=[
                            cql.Coordinate1Item(root=[-0.333333, 89.0]),
                            cql.Coordinate1Item(root=[-102.723546, -0.5]),
                            cql.Coordinate1Item(root=[-179.0, -89.0]),
                            cql.Coordinate1Item(root=[-1.9, 89.0]),
                            cql.Coordinate1Item(root=[-0.0, 89.0]),
                            cql.Coordinate1Item(root=[2.00001, -1.9]),
                            cql.Coordinate1Item(root=[-0.333333, 89.0]),
                        ]
                    )
                ]
            ),
            cql.PropertyRef(property="geometry"),
        ],
    )
    _assert_example("example46.json", expression)


def test_build_example47() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_DISJOINT,
        args=[
            cql.PropertyRef(property="geometry"),
            cql.Multipolygon(
                coordinates=[
                    [
                        cql.Coordinate4(
                            root=[
                                cql.Coordinate4Item(root=[144.022387, 45.176126]),
                                cql.Coordinate4Item(root=[-1.1, 0.0]),
                                cql.Coordinate4Item(root=[180.0, 47.808086]),
                                cql.Coordinate4Item(root=[144.022387, 45.176126]),
                            ]
                        )
                    ]
                ]
            ),
        ],
    )
    _assert_example("example47.json", expression)


def test_build_example48() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_TOUCHES,
        args=[
            cql.PropertyRef(property="geometry"),
            cql.Multilinestring(
                coordinates=[
                    cql.Coordinate3(
                        root=[
                            cql.Coordinate3Item(root=[-1.9, -0.99999]),
                            cql.Coordinate3Item(root=[75.292574, 1.5]),
                            cql.Coordinate3Item(root=[-0.5, -4.016458]),
                            cql.Coordinate3Item(root=[-31.708594, -74.743801]),
                            cql.Coordinate3Item(root=[179.0, -90.0]),
                        ]
                    ),
                    cql.Coordinate3(
                        root=[
                            cql.Coordinate3Item(root=[-1.9, -1.1]),
                            cql.Coordinate3Item(root=[1.5, 8.547371]),
                        ]
                    ),
                ]
            ),
        ],
    )
    _assert_example("example48.json", expression)


def test_build_example49() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_WITHIN,
        args=[
            cql.Polygon(
                coordinates=[
                    cql.Coordinate1(
                        root=[
                            cql.Coordinate1Item(root=[-49.88024, 0.5, -75993.341684]),
                            cql.Coordinate1Item(root=[-1.5, -0.99999, -100000.0]),
                            cql.Coordinate1Item(root=[0.0, 0.5, -0.333333]),
                            cql.Coordinate1Item(root=[-49.88024, 0.5, -75993.341684]),
                        ]
                    ),
                    cql.Coordinate1(
                        root=[
                            cql.Coordinate1Item(root=[-65.887123, 2.00001, -100000.0]),
                            cql.Coordinate1Item(root=[0.333333, -53.017711, -79471.332949]),
                            cql.Coordinate1Item(root=[180.0, 0.0, 1852.616704]),
                            cql.Coordinate1Item(root=[-65.887123, 2.00001, -100000.0]),
                        ]
                    ),
                ]
            ),
            cql.PropertyRef(property="geometry"),
        ],
    )
    _assert_example("example49.json", expression)


def test_build_example50() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_OVERLAPS,
        args=[
            cql.PropertyRef(property="geometry"),
            cql.BboxLiteral(bbox=[-179.912109, 1.9, 180.0, 16.897016]),
        ],
    )
    _assert_example("example50.json", expression)


def test_build_example51() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_CROSSES,
        args=[
            cql.PropertyRef(property="geometry"),
            cql.Linestring(
                coordinates=[
                    cql.Coordinate(root=[172.03086, 1.5]),
                    cql.Coordinate(root=[1.1, -90.0]),
                    cql.Coordinate(root=[-159.757695, 0.99999]),
                    cql.Coordinate(root=[-180.0, 0.5]),
                    cql.Coordinate(root=[-12.111235, 81.336403]),
                    cql.Coordinate(root=[-0.5, 64.43958]),
                    cql.Coordinate(root=[0.0, 81.991815]),
                    cql.Coordinate(root=[-155.93831, 90.0]),
                ]
            ),
        ],
    )
    _assert_example("example51.json", expression)


def test_build_example52() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_CONTAINS,
        args=[cql.PropertyRef(property="geometry"), cql.Point(coordinates=[-3.508362, -1.754181])],
    )
    _assert_example("example52.json", expression)


def test_build_example53() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_AFTER,
        args=[cql.PropertyRef(property="updated_at"), cql.DateInstant(date="2010-02-10")],
    )
    _assert_example("example53.json", expression)


def test_build_example54() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_BEFORE,
        args=[
            cql.PropertyRef(property="updated_at"),
            cql.TimestampInstant(timestamp="2012-08-10T05:30:00Z"),
        ],
    )
    _assert_example("example54.json", expression)


def test_build_example55() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_CONTAINS,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="2000-01-01T00:00:00Z"),
                    cql.TimestampString(root="2005-01-10T01:01:01.393216Z"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
        ],
    )
    _assert_example("example55.json", expression)


def test_build_example56() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_DISJOINT,
        args=[
            cql.IntervalInstance(
                interval=["..", cql.TimestampString(root="2005-01-10T01:01:01.393216Z")]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
        ],
    )
    _assert_example("example56.json", expression)


def test_build_example57() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_DURING,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[cql.DateString(root="2005-01-10"), cql.DateString(root="2010-02-10")]
            ),
        ],
    )
    _assert_example("example57.json", expression)


def test_build_example58() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_EQUALS,
        args=[cql.PropertyRef(property="updated_at"), cql.DateInstant(date="1851-04-29")],
    )
    _assert_example("example58.json", expression)


def test_build_example59() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_FINISHED_BY,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1991-10-07T08:21:06.393262Z"),
                    cql.TimestampString(root="2010-02-10T05:29:20.073225Z"),
                ]
            ),
        ],
    )
    _assert_example("example59.json", expression)


def test_build_example60() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_FINISHES,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.DateString(root="1991-10-07"),
                    cql.TimestampString(root="2010-02-10T05:29:20.073225Z"),
                ]
            ),
        ],
    )
    _assert_example("example60.json", expression)


def test_build_example61() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_INTERSECTS,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1991-10-07T08:21:06.393262Z"),
                    cql.TimestampString(root="2010-02-10T05:29:20.073225Z"),
                ]
            ),
        ],
    )
    _assert_example("example61.json", expression)


def test_build_example62() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_MEETS,
        args=[
            cql.IntervalInstance(
                interval=[cql.DateString(root="2005-01-10"), cql.DateString(root="2010-02-10")]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
        ],
    )
    _assert_example("example62.json", expression)


def test_build_example63() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_MET_BY,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="2010-02-10T05:29:20.073225Z"),
                    cql.DateString(root="2010-10-07"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
        ],
    )
    _assert_example("example63.json", expression)


def test_build_example64() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_OVERLAPPED_BY,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1991-10-07T08:21:06.393262Z"),
                    cql.TimestampString(root="2010-02-10T05:29:20.073225Z"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
        ],
    )
    _assert_example("example64.json", expression)


def test_build_example65() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_OVERLAPS,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1991-10-07T08:21:06.393262Z"),
                    cql.TimestampString(root="1992-10-09T08:08:08.393473Z"),
                ]
            ),
        ],
    )
    _assert_example("example65.json", expression)


def test_build_example66() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_STARTED_BY,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.TimestampString(root="1991-10-07T08:21:06.393262Z"),
                    cql.TimestampString(root="2010-02-10T05:29:20.073225Z"),
                ]
            ),
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
        ],
    )
    _assert_example("example66.json", expression)


def test_build_example67() -> None:
    expression = cql.TemporalPredicate(
        op=cql.TemporalPredicateOp.T_STARTS,
        args=[
            cql.IntervalInstance(
                interval=[
                    cql.PropertyRef(property="starts_at"),
                    cql.PropertyRef(property="ends_at"),
                ]
            ),
            cql.IntervalInstance(
                interval=[cql.TimestampString(root="1991-10-07T08:21:06.393262Z"), ".."]
            ),
        ],
    )
    _assert_example("example67.json", expression)


def test_build_example68() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[cql.FunctionRef(op="Foo", args=[cql.PropertyRef(property="geometry")]), True],
    )
    _assert_example("example68.json", expression)


def test_build_example69() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.NOT_EQUAL,
        args=[
            False,
            cql.FunctionRef(
                op="Bar", args=[cql.PropertyRef(property="geometry"), 100, "a", "b", False]
            ),
        ],
    )
    _assert_example("example69.json", expression)


def test_build_example70() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[cql.Accenti(args=[cql.PropertyRef(property="owner")]), cql.Accenti(args=["Beyoncé"])],
    )
    _assert_example("example70.json", expression)


def test_build_example71() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            cql.Casei(args=[cql.PropertyRef(property="owner")]),
            cql.Casei(args=["somebody else"]),
        ],
    )
    _assert_example("example71.json", expression)


def test_build_example72() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.GREATER_THAN,
        args=[
            cql.PropertyRef(property="value"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.ADD, args=[cql.PropertyRef(property="foo"), 10]
            ),
        ],
    )
    _assert_example("example72.json", expression)


def test_build_example73() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.LESS_THAN,
        args=[
            cql.PropertyRef(property="value"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.SUBTRACT, args=[cql.PropertyRef(property="foo"), 10]
            ),
        ],
    )
    _assert_example("example73.json", expression)


def test_build_example74() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.NOT_EQUAL,
        args=[
            cql.PropertyRef(property="value"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.MULTIPLY, args=[22.1, cql.PropertyRef(property="foo")]
            ),
        ],
    )
    _assert_example("example74.json", expression)


def test_build_example75() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            cql.PropertyRef(property="value"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.DIVIDE, args=[2, cql.PropertyRef(property="foo")]
            ),
        ],
    )
    _assert_example("example75.json", expression)


def test_build_example76() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.LESS_THAN_OR_EQUAL,
        args=[
            cql.PropertyRef(property="value"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.POWER, args=[2, cql.PropertyRef(property="foo")]
            ),
        ],
    )
    _assert_example("example76.json", expression)


def test_build_example77() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            0,
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.MODULO, args=[cql.PropertyRef(property="foo"), 2]
            ),
        ],
    )
    _assert_example("example77.json", expression)


def test_build_example78() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            1,
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.INTEGER_DIVIDE,
                args=[cql.PropertyRef(property="foo"), 2],
            ),
        ],
    )
    _assert_example("example78.json", expression)


def test_build_example79() -> None:
    expression = cql.ArrayPredicate(
        op=cql.ArrayPredicateOp.A_CONTAINED_BY,
        args=[cql.PropertyRef(property="values"), ["a", "b", "c"]],
    )
    _assert_example("example79.json", expression)


def test_build_example80() -> None:
    expression = cql.ArrayPredicate(
        op=cql.ArrayPredicateOp.A_CONTAINS,
        args=[cql.PropertyRef(property="values"), ["a", "b", "c"]],
    )
    _assert_example("example80.json", expression)


def test_build_example81() -> None:
    expression = cql.ArrayPredicate(
        op=cql.ArrayPredicateOp.A_EQUALS,
        args=[["a", True, 1.0, 8], cql.PropertyRef(property="values")],
    )
    _assert_example("example81.json", expression)


def test_build_example82() -> None:
    expression = cql.ArrayPredicate(
        op=cql.ArrayPredicateOp.A_OVERLAPS,
        args=[
            cql.PropertyRef(property="values"),
            [
                cql.TimestampInstant(timestamp="2012-08-10T05:30:00Z"),
                cql.DateInstant(date="2010-02-10"),
                False,
            ],
        ],
    )
    _assert_example("example82.json", expression)


def test_build_example83() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_EQUALS,
        args=[
            cql.Multipoint(
                coordinates=[
                    cql.Coordinate2(root=[180.0, -0.5]),
                    cql.Coordinate2(root=[179.0, -47.121701]),
                    cql.Coordinate2(root=[180.0, -0.0]),
                    cql.Coordinate2(root=[33.470475, -0.99999]),
                    cql.Coordinate2(root=[179.0, -15.333062]),
                ]
            ),
            cql.PropertyRef(property="geometry"),
        ],
    )
    _assert_example("example83.json", expression)


def test_build_example84() -> None:
    expression = cql.SpatialPredicate(
        op=cql.SpatialPredicateOp.S_EQUALS,
        args=[
            cql.Geometrycollection(
                geometries=[
                    cql.Point(coordinates=[1.9, 2.00001]),
                    cql.Point(coordinates=[0.0, -2.00001]),
                    cql.Multilinestring(
                        coordinates=[
                            cql.Coordinate3(
                                root=[
                                    cql.Coordinate3Item(root=[-2.00001, -0.0]),
                                    cql.Coordinate3Item(root=[-77.292642, -0.5]),
                                    cql.Coordinate3Item(root=[-87.515626, -0.0]),
                                    cql.Coordinate3Item(root=[-180.0, 12.502773]),
                                    cql.Coordinate3Item(root=[21.204842, -1.5]),
                                    cql.Coordinate3Item(root=[-21.878857, -90.0]),
                                ]
                            )
                        ]
                    ),
                    cql.Point(coordinates=[1.9, 0.5]),
                    cql.Linestring(
                        coordinates=[
                            cql.Coordinate(root=[179.0, 1.179148]),
                            cql.Coordinate(root=[-148.192487, -65.007816]),
                            cql.Coordinate(root=[0.5, 0.333333]),
                        ]
                    ),
                ]
            ),
            cql.PropertyRef(property="geometry"),
        ],
    )
    _assert_example("example84.json", expression)


def test_build_example85() -> None:
    expression = cql.BinaryComparisonPredicate(
        op=cql.BinaryComparisonPredicateOp.EQUAL,
        args=[
            cql.PropertyRef(property="value"),
            cql.ArithmeticExpression(
                op=cql.ArithmeticExpressionOp.SUBTRACT,
                args=[
                    cql.ArithmeticExpression(
                        op=cql.ArithmeticExpressionOp.ADD,
                        args=[
                            cql.ArithmeticExpression(
                                op=cql.ArithmeticExpressionOp.MULTIPLY,
                                args=[
                                    cql.ArithmeticExpression(
                                        op=cql.ArithmeticExpressionOp.MULTIPLY,
                                        args=[-1, cql.PropertyRef(property="foo")],
                                    ),
                                    2.0,
                                ],
                            ),
                            cql.ArithmeticExpression(
                                op=cql.ArithmeticExpressionOp.DIVIDE,
                                args=[cql.PropertyRef(property="bar"), 6.1234],
                            ),
                        ],
                    ),
                    cql.ArithmeticExpression(
                        op=cql.ArithmeticExpressionOp.POWER,
                        args=[cql.PropertyRef(property="x"), 2.0],
                    ),
                ],
            ),
        ],
    )
    _assert_example("example85.json", expression)


def test_build_example86() -> None:
    expression = cql.IsLikePredicate(
        args=(cql.PropertyRef(property="name"), cql.PatternExpression1(args=["FOO%"]))
    )
    _assert_example("example86.json", expression)
