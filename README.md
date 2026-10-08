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

[![PyPI - Version](https://img.shields.io/pypi/v/cql2json-pydantic.svg)](https://pypi.org/project/cql2json-pydantic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cql2json-pydantic.svg)](https://pypi.org/project/cql2json-pydantic)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/terradue/cql2json-pydantic/package.yaml?branch=develop&event=push&label=build&logo=githubactions)](https://github.com/terradue/cql2json-pydantic/actions/workflows/package.yaml?query=branch%3Adevelop)
[![Code coverage](https://img.shields.io/codecov/c/github/terradue/cql2json-pydantic/develop?logo=codecov)](https://app.codecov.io/gh/terradue/cql2json-pydantic/tree/develop)

Pydantic v2 models for building CQL2 JSON filters.

## Quick start

```console
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

See [more filter examples and their JSON output](docs/how-to/build-filter.md).

## Project conventions

This project is templated a Hatch-based Python package with:

- Apache-2.0 license
- Keep a Changelog-compatible `CHANGELOG.md`
- Diátaxis documentation under `docs/`
- top-level `mkdocs.yaml`
- Taskfile integration with `Terradue/taskfile-utils`
- GitHub Actions CI

## Documentation

Project documentation: https://terradue.github.io/cql2json-pydantic/

## Contribute

Submit a [Github issue](/issues) if you have comments or suggestions.

### Local quality checks

Install [Hatch](https://hatch.pypa.io/) and [Taskfiles](https://taskfile.dev/docs/guide) then install the Git hook:

```console
task quality:pre-commit:install
```

Every commit runs Ruff (including the configured McCabe complexity limit),
Ruff formatting, strict mypy checks, and the pytest suite.

Run the complete hook explicitly with:

```console
task quality:pre-commit:run
```

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
