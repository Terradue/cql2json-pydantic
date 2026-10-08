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


def test_array_predicate_serializes_nested_mixed_arrays() -> None:
    values = cql.Array(
        root=[
            "a",
            True,
            2.5,
            cql.DateInstant(date="2025-01-01"),
            cql.Array(root=[cql.Array(root=[]), cql.PropertyRef(property="value")]),
        ]
    )
    assert values.root[1] is True
    predicate = cql.ArrayPredicate(
        op=cql.ArrayPredicateOp.A_CONTAINS,
        args=[cql.PropertyRef(property="values"), values.root],
    )
    expected = {
        "op": "a_contains",
        "args": [
            {"property": "values"},
            ["a", True, 2.5, {"date": "2025-01-01"}, [[], {"property": "value"}]],
        ],
    }
    assert predicate.model_dump(mode="json", exclude_none=True, warnings="error") == expected
    restored = cql.ArrayPredicate.model_validate(expected)
    assert restored.model_dump(mode="json", exclude_none=True, warnings="error") == expected


def test_function_serializes_nested_array_arguments() -> None:
    function = cql.FunctionRef(
        op="custom",
        args=[
            [
                cql.Array(root=[cql.Array(root=["a"])]),
                cql.TimestampInstant(timestamp="2025-01-01T00:00:00Z"),
                False,
            ]
        ],
    )
    expected = {
        "op": "custom",
        "args": [[[["a"]], {"timestamp": "2025-01-01T00:00:00Z"}, False]],
    }
    assert function.model_dump(mode="json", exclude_none=True, warnings="error") == expected
    restored = cql.FunctionRef.model_validate(expected)
    assert restored.model_dump(mode="json", exclude_none=True, warnings="error") == expected


@pytest.mark.parametrize("values", [[], [[], [[]]]])
def test_array_accepts_empty_and_nested_json_arrays(values: list[object]) -> None:
    array = cql.Array.model_validate(values)
    assert array.model_dump(mode="json", warnings="error") == values


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (cql.Array, [None]),
        (cql.Array, [{"unexpected": "object"}]),
        (cql.ArrayPredicate, {"op": "a_contains", "args": [{"property": "values"}, [None]]}),
        (cql.FunctionRef, {"op": "custom", "args": [[None]]}),
    ],
)
def test_arrays_reject_values_outside_the_cql2_schema(
    model: type[BaseModel], payload: object
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)
